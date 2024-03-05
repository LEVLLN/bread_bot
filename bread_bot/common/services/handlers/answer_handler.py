import random
import re
import time

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
from bread_bot.common.services.member_service import ExternalMemberService, logger
from bread_bot.common.services.morph_service import MorphService
from bread_bot.common.utils.functions import composite_mask
from bread_bot.common.utils.structs import (
    AnswerEntityReactionTypesEnum,
    AnswerEntityContentTypesEnum,
)
from bread_bot.main.settings import IGNORED_USERS

morph = pymorphy2.MorphAnalyzer()

cached_keys: dict[int, dict[str, str]] = {}


class AnswerHandler(AbstractHandler):
    @property
    def condition(self) -> bool:
        return self.message_service and self.message_service.message and self.message_service.message.text

    def _find_keys(
        self, keys, reaction_type: AnswerEntityReactionTypesEnum, message_text: str | None = None
    ) -> list[str]:
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

    def _init_cached_keys(self):
        chat_id = self.member_service.chat.id
        if chat_id not in cached_keys:
            logger.info("Cached keys was inited for chat: %s", chat_id)
            cached_keys[chat_id] = {}
        return cached_keys

    def _get_morphed_words_to_keys(self, answer_keys: set) -> dict[str, str]:
        chat_id = self.member_service.chat.id
        for answer_key in answer_keys:
            cached_keys[chat_id][answer_key] = answer_key
            parsed_word = morph.parse(answer_key)[0]
            for item in parsed_word.lexeme:
                cached_keys[chat_id][item.word] = answer_key
        return cached_keys[chat_id]

    async def process_message(
        self,
        message_text: str | None = None,
    ) -> BaseAnswerSchema:
        raise NextStepException("Базовый класс")

    async def process(self) -> BaseAnswerSchema:
        raise NextStepException("Базовый класс")


class SubstringAnswerHandler(AnswerHandler):
    async def process_message(
        self,
        message_text: str | None = None,
    ) -> BaseAnswerSchema:
        if self.message_service.message.source.id in IGNORED_USERS:
            raise NextStepException("Пользователь игнорируется")
        self._init_cached_keys()
        start = time.time()
        exclude = set(cached_keys[self.member_service.chat.id].values())
        answer_keys = {
            answer_entity_key
            for answer_entity_key in await AnswerEntity.get_keys(
                db=self.db, pack_id=self.default_answer_pack.id, reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING
            )
            if answer_entity_key not in exclude
        }
        morphed_words_to_keys = self._get_morphed_words_to_keys(answer_keys)
        logger.info("Get morphed words time: %s", time.time() - start)

        if not morphed_words_to_keys:
            raise NextStepException("Значения не найдено")

        if message_text is not None:
            message_text = message_text.lower()
        else:
            message_text = self.message_service.message.text.lower()

        keys = set()
        start = time.time()
        substring_message_text = " " + message_text + " "

        for morphed_key, key_for_search in morphed_words_to_keys.items():
            if len(morphed_key) < 3:
                continue
            if " " + morphed_key + " " in substring_message_text:
                keys.add(key_for_search)
        logger.info("Search time: %s", time.time() - start)

        if not keys:
            raise NextStepException("Подходящих ключей не найдено")
        results = await AnswerEntity.async_filter(
            db=self.db,
            where=and_(
                AnswerEntity.pack_id == self.default_answer_pack.id,
                AnswerEntity.reaction_type == AnswerEntityReactionTypesEnum.SUBSTRING,
                AnswerEntity.key.in_(keys),
            ),
        )

        if not results:
            raise NextStepException("Значения не найдено")

        return self._choose_content(random.choice(results))

    async def process(self) -> BaseAnswerSchema:
        self.check_process_ability()
        if random.random() > self.default_answer_pack.answer_chance / 100:
            raise NextStepException("Пропуск ответа по проценту срабатывания")

        return await self.process_message()


class TriggerAnswerHandler(AnswerHandler):
    async def process_message(
        self,
        message_text: str | None = None,
    ) -> BaseAnswerSchema:
        start = time.time()
        if self.message_service.message.source.id in IGNORED_USERS:
            raise NextStepException("Пользователь игнорируется")
        answer_keys = {
            answer_entity_key
            for answer_entity_key in await AnswerEntity.get_keys(
                db=self.db, pack_id=self.default_answer_pack.id, reaction_type=AnswerEntityReactionTypesEnum.TRIGGER
            )
        }
        logger.info("Get morphed words time: %s", time.time() - start)

        if not answer_keys:
            raise NextStepException("Значения не найдено")

        if message_text is not None:
            message_text = message_text.lower()
        else:
            message_text = self.message_service.message.text.lower()

        keys = set()
        start = time.time()

        for key_for_search in answer_keys:
            if key_for_search == message_text:
                keys.add(key_for_search)
        logger.info("Search time: %s", time.time() - start)

        if not keys:
            raise NextStepException("Подходящих ключей не найдено")
        results = await AnswerEntity.async_filter(
            db=self.db,
            where=and_(
                AnswerEntity.pack_id == self.default_answer_pack.id,
                AnswerEntity.reaction_type == AnswerEntityReactionTypesEnum.TRIGGER,
                AnswerEntity.key.in_(keys),
            ),
        )

        if not results:
            raise NextStepException("Значения не найдено")

        return self._choose_content(random.choice(results))

    async def process(self) -> BaseAnswerSchema:
        self.check_process_ability()
        return await self.process_message()


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
        if self.message_service.message.source.id in IGNORED_USERS:
            raise NextStepException("Пользователь игнорируется")
        if random.random() > self.member_service.chat.morph_answer_chance / 100:
            raise NextStepException("Пропуск ответа по проценту срабатывания")
        return await self.process_morph()
