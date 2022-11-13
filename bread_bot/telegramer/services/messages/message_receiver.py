import logging
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.exceptions.base import NextStepException, RaiseUpException
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.schemas.telegram_messages import StandardBodySchema
from bread_bot.telegramer.services.handlers.command_handler import CommandHandler
from bread_bot.telegramer.services.handlers.handler import EmptyResultHandler
from bread_bot.telegramer.services.member_service import MemberService
from bread_bot.telegramer.services.messages.message_service import MessageService

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
                return TextAnswerSchema(
                    text=str(raise_ex),
                    chat_id=self.request_body.message.chat.id,
                    reply_to_message_id=self.request_body.message.message_id,
                )
            except Exception as e:
                logger.error("Error while handle process", exc_info=e)
                return None
            else:
                return result

        return wrapper

    @fallback_method
    async def receive(self):
        message_service: MessageService = MessageService(request_body=self.request_body)
        member_service: MemberService = MemberService(db=self.db, message=message_service.message)
        await member_service.process()

        handler = CommandHandler(EmptyResultHandler(None))
        result = await handler.handle(self.db, message_service, member_service)

        return result
