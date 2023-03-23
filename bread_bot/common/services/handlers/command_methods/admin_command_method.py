import logging

from sqlalchemy import and_

from bread_bot.common.exceptions.base import RaiseUpException, NextStepException
from bread_bot.common.models import (
    AnswerPack,
    AnswerEntity,
)
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.schemas.commands import (
    CommandSchema,
    ValueCommandSchema,
)
from bread_bot.common.services.handlers.answer_handler import (
    AnswerHandler,
)
from bread_bot.common.services.handlers.command_methods.base_command_method import BaseCommandMethod
from bread_bot.common.utils.structs import (
    AdminCommandsEnum,
    ANSWER_ENTITY_MAP,
    AnswerEntityReactionTypesEnum,
    AnswerEntityContentTypesEnum,
)

logger = logging.getLogger(__name__)


class AdminCommandMethod(BaseCommandMethod):
    async def execute(self) -> TextAnswerSchema:
        match self.command_instance.command:
            case AdminCommandsEnum.ADD:
                return await self.add(
                    key=self.command_instance.key,
                    value=self.command_instance.value,
                    content_type=AnswerEntityContentTypesEnum.TEXT,
                    reaction_type=ANSWER_ENTITY_MAP[self.command_instance.parameter],
                )
            case AdminCommandsEnum.SHOW:
                return await self.show()
            case AdminCommandsEnum.REMEMBER:
                return await self.remember(reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING)
            case AdminCommandsEnum.REMEMBER_TRIGGER:
                return await self.remember(reaction_type=AnswerEntityReactionTypesEnum.TRIGGER)
            case AdminCommandsEnum.DELETE:
                return await self.delete()
            case AdminCommandsEnum.ANSWER_CHANCE:
                return await self.handle_answer_chance()
            case AdminCommandsEnum.CHECK_ANSWER:
                return await self.check_answer()
            case AdminCommandsEnum.SAY:
                return await self.say()
            case AdminCommandsEnum.SHOW_KEYS:
                return await self.show_keys()
            case _:
                raise NextStepException("Не найдена команда")

    async def show(self):
        raise RaiseUpException("Функция временно отключена")

    async def add(
        self,
        key: str,
        value: str,
        content_type: AnswerEntityContentTypesEnum,
        reaction_type: AnswerEntityReactionTypesEnum,
        description: str | None = None,
    ):
        """Команда Добавить"""
        self._check_length_key(reaction_type, key)

        if not self.default_answer_pack:
            self.default_answer_pack: AnswerPack = await AnswerPack.create_by_chat_id(
                self.db, self.member_service.chat.id
            )
        entity = await AnswerEntity.async_first(
            self.db,
            where=and_(
                AnswerEntity.key == key.lower(),
                AnswerEntity.value == value,
                AnswerEntity.pack_id == self.default_answer_pack.id,
                AnswerEntity.reaction_type == reaction_type,
                AnswerEntity.content_type == content_type,
            ),
            for_update=True,
        )
        if entity is None:
            instance_params = dict(
                pack_id=self.default_answer_pack.id,
                key=key.lower(),
                value=value,
                reaction_type=reaction_type,
                content_type=content_type,
            )
            if description is not None:
                instance_params.update(dict(description=description))
            await AnswerEntity.async_add(db=self.db, instance=AnswerEntity(**instance_params))
        return super()._return_answer()

    async def remember(self, reaction_type: AnswerEntityReactionTypesEnum = AnswerEntityReactionTypesEnum.SUBSTRING):
        """Команда Запомни"""
        self._check_reply_existed()
        reply = self.message_service.message.reply
        value, content_type, description = self.message_service.select_content_from_message(reply)

        if not self.default_answer_pack:
            self.default_answer_pack: AnswerPack = await AnswerPack.create_by_chat_id(
                self.db, self.member_service.chat.id
            )
        entities = []
        keys_to_skip = [
            entity.key
            for entity in await AnswerEntity.async_filter(
                db=self.db,
                where=and_(
                    AnswerEntity.pack_id == self.default_answer_pack.id,
                    AnswerEntity.key.in_(self.command_instance.value_list),
                    AnswerEntity.value == value,
                    AnswerEntity.content_type == content_type,
                ),
            )
        ]

        for key in self.command_instance.value_list:
            self._check_length_key(reaction_type, key)
            if key in keys_to_skip:
                continue
            instance_params = dict(
                pack_id=self.default_answer_pack.id,
                key=key.lower(),
                value=value,
                content_type=content_type,
                reaction_type=reaction_type,
            )
            if description is not None:
                instance_params.update(dict(description=description))
            entities.append(AnswerEntity(**instance_params))

        await AnswerEntity.async_add_all(db=self.db, instances=entities)

        return super()._return_answer()

    async def delete(self):
        """Удаление по ключам и по ключам-значениям"""
        return super()._return_answer("Фича временно отключена. В процессе доработки.")

    async def handle_answer_chance(self):
        if not self.default_answer_pack:
            self.default_answer_pack: AnswerPack = await AnswerPack.create_by_chat_id(
                self.db, self.member_service.chat.id
            )
        match self.command_instance:
            case ValueCommandSchema():
                chance_value = self.command_instance.value
                error_message = "Некорректное значение. Необходимо ввести число от 0 до 100"
                try:
                    value = int(chance_value.strip())
                except (ValueError, AttributeError):
                    return super()._return_answer(error_message)
                if value > 100 or value < 0:
                    return super()._return_answer(error_message)
                self.default_answer_pack.answer_chance = value
                await AnswerPack.async_add(db=self.db, instance=self.default_answer_pack)
                return super()._return_answer()
            case CommandSchema():
                return super()._return_answer(str(self.default_answer_pack.answer_chance))
            case _:
                raise RaiseUpException("Не удалось установить процент срабатывания")

    async def check_answer(self):
        if not isinstance(self.command_instance, ValueCommandSchema):
            return super()._return_answer("Необходимо указать параметром, что надо искать")

        result = None
        for reaction_type in (AnswerEntityReactionTypesEnum.TRIGGER, AnswerEntityReactionTypesEnum.SUBSTRING):
            handler = AnswerHandler(next_handler=None)
            handler.db = self.db
            handler.message_service = self.message_service
            handler.default_answer_pack = self.default_answer_pack
            handler.member_service = self.member_service

            try:
                handler.check_process_ability(check_edited_message=False)
                result = await handler.process_message(
                    reaction_type=reaction_type, message_text=self.command_instance.value
                )
            except NextStepException as e:
                logger.error("Error: %s %s", self.__class__.__name__, str(e))
                continue
        if result is None:
            return super()._return_answer("Ничего не было найдено")
        return result

    async def say(self):
        if not isinstance(self.command_instance, ValueCommandSchema):
            return super()._return_answer("Необходимо указать параметром, что надо сказать")
        return super()._return_answer(self.command_instance.value)

    async def show_keys(self):
        self._check_reply_existed()
        reply = self.message_service.message.reply
        value, content_type, description = self.message_service.select_content_from_message(reply)
        answer_entities = await AnswerEntity.async_filter(
            db=self.db,
            where=and_(
                AnswerEntity.pack_id == self.default_answer_pack.id,
                AnswerEntity.value == value,
                AnswerEntity.content_type == content_type,
                AnswerEntity.description == description,
            ),
        )
        if not answer_entities:
            return super()._return_answer("Не найдено ключей на выбранный контент")

        key_list = ", ".join([answer_entity.key for answer_entity in answer_entities])
        return super()._return_answer(f"Перечень ключей на значение: [{key_list}]")
