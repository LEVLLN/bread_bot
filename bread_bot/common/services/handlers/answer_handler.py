import random
import re

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
from bread_bot.common.utils.functions import composite_mask
from bread_bot.common.utils.structs import (
    AnswerEntityTypesEnum,
    AnswerEntityContentTypesEnum,
)


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
        entities = await AnswerEntity.async_filter(
            self.db,
            where=and_(
                AnswerEntity.pack_id == self.default_answer_pack.id,
                AnswerEntity.reaction_type == reaction_type,
            ),
        )
        for entity in entities:
            if entity.key not in answer_pack_by_keys:
                answer_pack_by_keys[entity.key] = [
                    entity,
                ]
                continue
            answer_pack_by_keys[entity.key].append(entity)
        if not answer_pack_by_keys:
            raise NextStepException("Нет значений")
        keys = self.find_keys(answer_pack_by_keys=answer_pack_by_keys, reaction_type=reaction_type)

        result: None = None
        for key in keys:
            try:
                results = answer_pack_by_keys[key]
            except KeyError:
                continue
            result: AnswerEntity = random.choice(results)
            break
        if result is None:
            raise NextStepException("Значения не найдено")

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

    async def process(self) -> BaseAnswerSchema:
        raise NextStepException("Базовый класс")


class SubstringAnswerHandler(AnswerHandler):
    async def process(self) -> BaseAnswerSchema:
        return await super().process_message(reaction_type=AnswerEntityTypesEnum.SUBSTRING)


class TriggerAnswerHandler(AnswerHandler):
    async def process(self) -> BaseAnswerSchema:
        return await super().process_message(reaction_type=AnswerEntityTypesEnum.TRIGGER)
