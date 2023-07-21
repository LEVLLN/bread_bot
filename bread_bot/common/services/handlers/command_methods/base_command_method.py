import random

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.exceptions.base import RaiseUpException
from bread_bot.common.models import AnswerPack
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.schemas.commands import (
    CommandSchema,
    KeyValueParameterCommandSchema,
    ValueListCommandSchema,
    ValueCommandSchema,
    ParameterCommandSchema,
    ValueListParameterCommandSchema,
)
from bread_bot.common.schemas.telegram_messages import BaseMessageSchema
from bread_bot.common.services.member_service import MemberService
from bread_bot.common.services.messages.message_service import MessageService
from bread_bot.common.utils.structs import (
    AnswerEntityReactionTypesEnum,
    AnswerEntityContentTypesEnum,
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

    COMPLETE_MESSAGES = ["Сделал", "Слушаю и повинуюсь", "Есть, сэр!", "Выполнено", "Принял"]

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

    @classmethod
    def _select_content_from_reply(
        cls, reply: BaseMessageSchema
    ) -> tuple[str, AnswerEntityContentTypesEnum, str | None]:
        description = None
        if reply.voice:
            value = reply.voice.file_id
            content_type = AnswerEntityContentTypesEnum.VOICE
        elif reply.photo:
            value = reply.photo[0].file_id
            description = reply.caption
            content_type = AnswerEntityContentTypesEnum.PICTURE
        elif reply.sticker:
            value = reply.sticker.file_id
            content_type = AnswerEntityContentTypesEnum.STICKER
        elif reply.video:
            value = reply.video.file_id
            content_type = AnswerEntityContentTypesEnum.VIDEO
        elif reply.video_note:
            value = reply.video_note.file_id
            content_type = AnswerEntityContentTypesEnum.VIDEO_NOTE
        elif reply.animation:
            value = reply.animation.file_id
            content_type = AnswerEntityContentTypesEnum.ANIMATION
        elif reply.text:
            value = reply.text
            content_type = AnswerEntityContentTypesEnum.TEXT
        else:
            raise RaiseUpException("Данный тип данных не поддерживается")
        return value, content_type, description
