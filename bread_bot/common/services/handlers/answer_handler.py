import random
import re
from functools import lru_cache

import pymorphy2
from sqlalchemy import and_

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.models import (
    AnswerEntity,
)
from bread_bot.common.schemas.bread_bot_answers import (
    BaseAnswerSchema,
    TextAnswerSchema,
    PhotoAnswerSchema,
    StickerAnswerSchema,
    VoiceAnswerSchema,
    GifAnswerSchema,
    VideoAnswerSchema,
    VideoNoteAnswerSchema,
)
from bread_bot.common.services.handlers.handler import AbstractHandler
from bread_bot.common.services.member_service import ExternalMemberService
from bread_bot.common.utils.functions import composite_mask
from bread_bot.common.utils.structs import (
    AnswerEntityReactionTypesEnum,
    AnswerEntityContentTypesEnum,
)

morph = pymorphy2.MorphAnalyzer()


@lru_cache()
def get_morphed_words_to_keys(answer_keys: tuple) -> dict[str, str]:
    morphed_words_to_keys = {}
    for answer_key in answer_keys:
        parsed_word = morph.parse(answer_key)[0]
        for item in parsed_word.lexeme:
            morphed_words_to_keys[item.word] = answer_key
    return morphed_words_to_keys


class AnswerHandler(AbstractHandler):
    @property
    def condition(self) -> bool:
        return self.message_service and self.message_service.message and self.message_service.message.text

    def _find_keys(self, keys, reaction_type: AnswerEntityReactionTypesEnum, message_text: str | None = None):
        """Поиск ключей из БД среди сообщения"""
        match reaction_type:
            case AnswerEntityReactionTypesEnum.SUBSTRING:
                regex = f"({composite_mask(keys, split=True)})"
            case AnswerEntityReactionTypesEnum.TRIGGER:
                regex = f"^({composite_mask(keys)})$"
            case _:
                raise NextStepException("Неподходящий тип данных")

        if message_text is not None:
            message_text = message_text.lower()
        else:
            message_text = self.message_service.message.text.lower()

        groups = re.findall(regex, message_text, re.IGNORECASE)
        if len(groups) == 0:
            raise NextStepException("Подходящих ключей не найдено")
        return groups

    def check_process_ability(self, check_edited_message: bool = True):
        if not self.condition:
            raise NextStepException("Не подходит условие для обработки")
        if check_edited_message and self.message_service.has_edited_message:
            raise NextStepException("Пропуск отредактированного сообщения")
        if not self.default_answer_pack:
            raise NextStepException("Отсутствуют пакеты с ответами")

    def _choose_content(self, result: AnswerEntity):
        base_message_params = dict(
            reply_to_message_id=self.message_service.message.message_id,
            chat_id=self.message_service.message.chat.id,
        )
        match result.content_type:
            case AnswerEntityContentTypesEnum.TEXT:
                return TextAnswerSchema(**base_message_params, text=result.value)
            case AnswerEntityContentTypesEnum.PICTURE:
                return PhotoAnswerSchema(**base_message_params, photo=result.value, caption=result.description)
            case AnswerEntityContentTypesEnum.STICKER:
                return StickerAnswerSchema(**base_message_params, sticker=result.value)
            case AnswerEntityContentTypesEnum.VOICE:
                return VoiceAnswerSchema(**base_message_params, voice=result.value)
            case AnswerEntityContentTypesEnum.ANIMATION:
                return GifAnswerSchema(**base_message_params, animation=result.value)
            case AnswerEntityContentTypesEnum.VIDEO:
                return VideoAnswerSchema(**base_message_params, video=result.value)
            case AnswerEntityContentTypesEnum.VIDEO_NOTE:
                return VideoNoteAnswerSchema(**base_message_params, video_note=result.value)
            case _:
                raise NextStepException("Полученный тип контента не подлежит ответу")

    async def process_message(
        self,
        reaction_type: AnswerEntityReactionTypesEnum,
        message_text: str | None = None,
    ) -> BaseAnswerSchema:
        answer_keys = tuple(
            await AnswerEntity.get_keys(db=self.db, pack_id=self.default_answer_pack.id, reaction_type=reaction_type)
        )
        morphed_words_to_keys = get_morphed_words_to_keys(answer_keys)

        if not morphed_words_to_keys:
            raise NextStepException("Значения не найдено")

        keys = self._find_keys(
            keys=morphed_words_to_keys.keys(), reaction_type=reaction_type, message_text=message_text
        )
        results = None
        for key in keys:
            results = await AnswerEntity.async_filter(
                db=self.db,
                where=and_(
                    AnswerEntity.pack_id == self.default_answer_pack.id,
                    AnswerEntity.reaction_type == reaction_type,
                    AnswerEntity.key == morphed_words_to_keys[key],
                ),
            )
            if results:
                break

        if not results:
            raise NextStepException("Значения не найдено")

        return self._choose_content(random.choice(results))

    async def process(self) -> BaseAnswerSchema:
        raise NextStepException("Базовый класс")


class SubstringAnswerHandler(AnswerHandler):
    async def process(self) -> BaseAnswerSchema:
        self.check_process_ability()
        if random.random() > self.default_answer_pack.answer_chance / 100:
            raise NextStepException("Пропуск ответа по проценту срабатывания")

        return await super().process_message(reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING)


class TriggerAnswerHandler(AnswerHandler):
    async def process(self) -> BaseAnswerSchema:
        self.check_process_ability()
        if random.random() > self.default_answer_pack.answer_chance / 100:
            raise NextStepException("Пропуск ответа по проценту срабатывания")

        return await super().process_message(reaction_type=AnswerEntityReactionTypesEnum.TRIGGER)


class PictureAnswerHandler(AnswerHandler):
    @property
    def condition(self) -> bool:
        return self.message_service and self.message_service.message and self.message_service.message.photo

    async def _who_on_picture(self):
        username = await ExternalMemberService(self.db, self.member_service, self.message_service).get_one_of_group()
        return TextAnswerSchema(
            reply_to_message_id=self.message_service.message.message_id,
            chat_id=self.message_service.message.chat.id,
            text=f"Похоже на {username}",
        )

    async def process_picture(self) -> BaseAnswerSchema:
        return await self._who_on_picture()

    async def process(self) -> BaseAnswerSchema:
        self.check_process_ability()
        if random.random() > 20 / 100:
            raise NextStepException("Пропуск ответа по проценту срабатывания")

        return await self.process_picture()
