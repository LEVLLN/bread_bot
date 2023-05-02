import random

import pymorphy2
from sqlalchemy import and_

from bread_bot.common.exceptions.base import NextStepException, RaiseUpException
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
from bread_bot.common.services.morph_service import MorphService
from bread_bot.common.utils.structs import (
    AnswerEntityReactionTypesEnum,
    AnswerEntityContentTypesEnum,
)

morph = pymorphy2.MorphAnalyzer()

morphed_keys_cache = {}


class AnswerHandler(AbstractHandler):
    @property
    def condition(self) -> bool:
        return self.message_service and self.message_service.message and self.message_service.message.text

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

    def _get_excluded_keys(self) -> set[str]:
        chat_id = self.member_service.chat.id
        if chat_id not in morphed_keys_cache:
            morphed_keys_cache[chat_id] = {}
        return morphed_keys_cache[chat_id].values()

    def _get_morphed_words_to_keys(self, answer_keys: set) -> dict[str, str]:
        chat_id = self.member_service.chat.id
        for answer_key in answer_keys:
            morphed_keys_cache[chat_id][answer_key] = answer_key
            parsed_word = morph.parse(answer_key)[0]
            for item in parsed_word.lexeme:
                morphed_keys_cache[chat_id][item.word] = answer_key
        return morphed_keys_cache[chat_id]

    def _check_substring(self, word: str, message_list: list[str]) -> bool:
        if len(word) < 3:
            raise NextStepException("Подходящих ключей не найдено")
        return word in message_list

    def _check_trigger(self, word: str, message_text: str) -> bool:
        return word == message_text

    async def process_message(
        self,
        reaction_type: AnswerEntityReactionTypesEnum,
        message_text: str | None = None,
    ) -> BaseAnswerSchema:
        answer_keys = {
            answer_entity_key
            for answer_entity_key in await AnswerEntity.get_keys(
                db=self.db,
                pack_id=self.default_answer_pack.id,
                reaction_type=reaction_type,
                exclude_keys=self._get_excluded_keys(),
            )
        }
        morphed_words_to_keys = self._get_morphed_words_to_keys(answer_keys)

        if not morphed_words_to_keys:
            raise NextStepException("Значения не найдено")

        if message_text is not None:
            message_text = message_text.lower()
        else:
            message_text = self.message_service.message.text.lower()

        if reaction_type is AnswerEntityReactionTypesEnum.SUBSTRING:
            check_method = self._check_substring
            message_text = message_text.split()
        elif reaction_type is AnswerEntityReactionTypesEnum.TRIGGER:
            check_method = self._check_trigger
        else:
            raise NextStepException("Неподходящий тип данных")

        keys = []
        for string in sorted(morphed_words_to_keys.keys(), key=len, reverse=True):
            if check_method(string, message_text):
                keys.append(morphed_words_to_keys[string])

        if not keys:
            raise NextStepException("Подходящих ключей не найдено")

        results = await AnswerEntity.async_filter(
            db=self.db,
            where=and_(
                AnswerEntity.pack_id == self.default_answer_pack.id,
                AnswerEntity.reaction_type == reaction_type,
                AnswerEntity.key.in_(keys),
            ),
        )
        print(results, keys)
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


class MorphAnswerHandler(AnswerHandler):
    async def process_morph(self) -> BaseAnswerSchema:
        text = self.message_service.message.text or self.message_service.message.caption
        if not text:
            raise NextStepException("Контент не поддерживается")
        try:
            result = await MorphService(self.db, chat_id=self.member_service.chat.id).morph_text(text)
        except RaiseUpException as e:
            raise NextStepException(str(e))
        else:
            if result == text:
                raise NextStepException("Нового значения не сгенерировалось")
            return TextAnswerSchema(
                text=result,
                reply_to_message_id=self.message_service.message.message_id,
                chat_id=self.message_service.message.chat.id,
            )

    async def process(self) -> BaseAnswerSchema:
        if random.random() > self.member_service.chat.morph_answer_chance / 100:
            raise NextStepException("Пропуск ответа по проценту срабатывания")
        return await self.process_morph()
