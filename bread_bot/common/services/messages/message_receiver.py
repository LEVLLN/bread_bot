import logging
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.exceptions.base import NextStepException, RaiseUpException
from bread_bot.common.models import AnswerPack
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema, BaseAnswerSchema
from bread_bot.common.schemas.telegram_messages import StandardBodySchema
from bread_bot.common.services.handlers.answer_handler import (
    TriggerAnswerHandler,
    SubstringAnswerHandler,
    PictureAnswerHandler,
)
from bread_bot.common.services.handlers.command_handler import CommandHandler
from bread_bot.common.services.handlers.handler import EmptyResultHandler
from bread_bot.common.services.member_service import MemberService
from bread_bot.common.services.messages.message_service import MessageService

logger = logging.getLogger(__name__)


class MessageReceiver:
    def __init__(self, db: AsyncSession, request_body: StandardBodySchema):
        self.db: AsyncSession = db
        self.request_body: StandardBodySchema = request_body

    @staticmethod
    def fallback_method(func):
        """
        Декоратор мягкой обработки функции для ответа на сообщение
        """

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                if not args and not kwargs:
                    result = await func(self)
                else:
                    result = await func(self, *args, **kwargs)
            except NextStepException:
                return None
            except RaiseUpException as raise_ex:
                if self.request_body and self.request_body.message and self.request_body.message.chat:
                    return TextAnswerSchema(
                        text=str(raise_ex),
                        chat_id=self.request_body.message.chat.id,
                        reply_to_message_id=self.request_body.message.message_id,
                    )
                else:
                    return None
            except Exception as e:
                logger.error("Error while handle process", exc_info=e)
                return None
            else:
                return result

        return wrapper

    @fallback_method
    async def receive(self) -> BaseAnswerSchema | None:
        message_service: MessageService = MessageService(request_body=self.request_body)
        member_service: MemberService = MemberService(db=self.db, message=message_service.message)

        await member_service.process()

        default_answer_pack: AnswerPack = await AnswerPack.get_by_chat_id(
            db=self.db,
            chat_id=member_service.chat.id,
        )

        handler = CommandHandler(
            TriggerAnswerHandler(SubstringAnswerHandler(PictureAnswerHandler(EmptyResultHandler(None))))
        )
        return await handler.handle(self.db, message_service, member_service, default_answer_pack)
