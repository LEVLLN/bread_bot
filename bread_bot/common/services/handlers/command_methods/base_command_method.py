import random

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.exceptions.base import RaiseUpException
from bread_bot.common.models import AnswerPack
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.schemas.commands import (
    CommandSchema,
    KeyValueParameterCommandSchema,
    ParameterCommandSchema,
    ValueCommandSchema,
    ValueListCommandSchema,
    ValueListParameterCommandSchema,
)
from bread_bot.common.services.member_service import MemberService
from bread_bot.common.services.messages.message_service import MessageService
from bread_bot.common.utils.structs import (
    AnswerEntityReactionTypesEnum,
)

COMMAND_INSTANCE_TYPE = (
    CommandSchema
    | ValueCommandSchema
    | ValueListCommandSchema
    | ValueListParameterCommandSchema
    | ParameterCommandSchema
    | KeyValueParameterCommandSchema
)


class BaseCommandMethod:
    def __init__(
        self,
        db: AsyncSession,
        command_instance: COMMAND_INSTANCE_TYPE,
        message_service: MessageService,
        member_service: MemberService,
        default_answer_pack: AnswerPack | None = None,
    ):
        self.db: AsyncSession = db
        self.command_instance: COMMAND_INSTANCE_TYPE = command_instance
        self.member_service: MemberService = member_service
        self.message_service: MessageService = message_service
        self.default_answer_pack: AnswerPack = default_answer_pack

    COMPLETE_MESSAGES = ["Сделал", "Есть, сэр!", "Выполнено", "Принял"]

    def _return_answer(self, text: str | None = None):
        """Вернуть текстовый ответ пользователю"""
        return TextAnswerSchema(
            text=text or random.choice(self.COMPLETE_MESSAGES),
            chat_id=self.member_service.chat.chat_id,
            reply_to_message_id=self.message_service.message.message_id,
        )

    @staticmethod
    def _check_length_key(reaction_type: AnswerEntityReactionTypesEnum, key: str):
        """Обязательная проверка ключей"""
        if reaction_type != AnswerEntityReactionTypesEnum.TRIGGER and len(key) < 3:
            raise RaiseUpException("Ключ для подстроки не может быть меньше 3-х символов")

    def _check_reply_existed(self):
        """Обязательная проверка значения"""
        if self.message_service.message.reply is None:
            raise RaiseUpException("Необходимо выбрать сообщение в качестве ответа для обработки")
