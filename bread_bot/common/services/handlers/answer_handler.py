import asyncio
import functools
import operator
import random
import re

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.models import (
    TextEntity,
    VoiceEntity,
    PhotoEntity,
    StickerEntity,
    GifEntity,
    VideoEntity,
    VideoNoteEntity,
    AnswerPack,
)
from bread_bot.common.models.answer_entities.base_answer_entities import BaseEntity
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
from bread_bot.common.utils.functions import composite_mask
from bread_bot.common.utils.structs import (
    AnswerEntityTypesEnum,
)


def async_lru_cache_decorator(async_function):
    @functools.lru_cache
    def cached_async_function(*args, **kwargs):
        coroutine = async_function(*args, **kwargs)
        return asyncio.ensure_future(coroutine)

    return cached_async_function


def async_lru_cache(*lru_cache_args, **lru_cache_kwargs):
    def async_lru_cache_decorator(async_function):
        @functools.lru_cache(*lru_cache_args, **lru_cache_kwargs)
        def cached_async_function(*args, **kwargs):
            coroutine = async_function(*args, **kwargs)
            return asyncio.ensure_future(coroutine)

        return cached_async_function

    return async_lru_cache_decorator


@async_lru_cache(maxsize=512)
async def get_entities(db: AsyncSession, answer_pack: AnswerPack) -> list[BaseEntity]:
    params = []
    for entity_class in [
        TextEntity,
        GifEntity,
        VideoEntity,
        VideoNoteEntity,
        PhotoEntity,
        StickerEntity,
        VoiceEntity,
    ]:
        params.append(
            entity_class.async_filter(
                db,
                where=entity_class.pack_id == answer_pack.id,
            )
        )
    return list(functools.reduce(operator.iconcat, await asyncio.gather(*params), []))


class AnswerHandler(AbstractHandler):
    async def condition(self) -> bool:
        return (
            self.message_service
            and self.message_service.message
            and self.message_service.message.text
            and not self.message_service.has_edited_message
        )

    def find_keys(self, answer_pack_by_keys: dict, reaction_type: AnswerEntityTypesEnum):
        """Поиск ключей из БД среди сообщения"""
        match reaction_type:
            case AnswerEntityTypesEnum.SUBSTRING:
                regex = f"({composite_mask(list(answer_pack_by_keys.keys()), split=True)})"
            case AnswerEntityTypesEnum.TRIGGER:
                regex = f"^({composite_mask(list(answer_pack_by_keys.keys()))})$"
            case _:
                raise NextStepException("Неподходящий тип данных")
        groups = re.findall(regex, self.message_service.message.text.lower(), re.IGNORECASE)
        if len(groups) == 0:
            raise NextStepException("Подходящих ключей не найдено")
        return groups

    async def process_message(self, reaction_type: AnswerEntityTypesEnum) -> BaseAnswerSchema:
        if not await self.condition():
            raise NextStepException("Не подходит условие для обработки")

        if not self.default_answer_pack:
            raise NextStepException("Отсутствуют пакеты с ответами")
        # Отработка шансов только для подстрок
        if random.random() > self.default_answer_pack.answer_chance / 100:
            raise NextStepException("Пропуск ответа по проценту срабатывания")

        answer_pack_by_keys = {}
        for entity in await get_entities(db=self.db, answer_pack=self.default_answer_pack):
            if entity.reaction_type != reaction_type:
                continue
            if entity.key not in answer_pack_by_keys:
                answer_pack_by_keys[entity.key] = [
                    entity,
                ]
                continue
            answer_pack_by_keys[entity.key].append(entity)
        if not answer_pack_by_keys:
            raise NextStepException("Нет значений")
        keys = self.find_keys(answer_pack_by_keys=answer_pack_by_keys, reaction_type=reaction_type)

        result = None
        for key in keys:
            try:
                results = answer_pack_by_keys[key]
            except KeyError:
                continue
            result = random.choice(results)
            break
        if result is None:
            raise NextStepException("Значения не найдено")

        base_message_params = dict(
            reply_to_message_id=self.message_service.message.message_id,
            chat_id=self.message_service.message.chat.id,
        )
        match result:
            case TextEntity():
                return TextAnswerSchema(**base_message_params, text=result.value)
            case PhotoEntity():
                return PhotoAnswerSchema(**base_message_params, photo=result.value, caption=result.description)
            case StickerEntity():
                return StickerAnswerSchema(**base_message_params, sticker=result.value)
            case VoiceEntity():
                return VoiceAnswerSchema(**base_message_params, voice=result.value)
            case GifEntity():
                return GifAnswerSchema(**base_message_params, animation=result.value)
            case VideoEntity():
                return VideoAnswerSchema(**base_message_params, video=result.value)
            case VideoNoteEntity():
                return VideoNoteAnswerSchema(**base_message_params, video_note=result.value)
            case _:
                raise NextStepException("Полученный тип контента не подлежит ответу")

    async def process(self) -> BaseAnswerSchema:
        raise NextStepException("Базовый класс")


class SubstringAnswerHandler(AnswerHandler):
    async def process(self) -> BaseAnswerSchema:
        return await super().process_message(reaction_type=AnswerEntityTypesEnum.SUBSTRING)


class TriggerAnswerHandler(AnswerHandler):
    async def process(self) -> BaseAnswerSchema:
        return await super().process_message(reaction_type=AnswerEntityTypesEnum.TRIGGER)
