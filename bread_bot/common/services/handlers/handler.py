import logging

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.schemas.bread_bot_answers import BaseAnswerSchema
from bread_bot.common.services.member_service import MemberService
from bread_bot.common.services.messages.message_service import MessageService

logger = logging.getLogger(__name__)


class AbstractHandler:
    """Абстрактный класс обработчиков"""

    def __init__(self, next_handler):
        self._next_handler = next_handler
        self.message_service: MessageService | None = None
        self.member_service: MemberService | None = None
        self.db: AsyncSession | None = None

    @property
    def condition(self) -> bool:
        return True

    async def handle(
        self,
        db: AsyncSession,
        message_service: MessageService,
        member_service: MemberService,
    ) -> BaseAnswerSchema | None:
        self.db = db
        self.message_service = message_service
        self.member_service = member_service

        try:
            result = await self.process()
        except NextStepException as e:
            logger.info("Пропуск обработки %s: %s", self.__class__.__name__, *e.args)
            if self._next_handler is not None:
                return await self._next_handler.handle(db, message_service, member_service)
        else:
            return result

        raise NextStepException("Остановка обработки")

    async def process(self) -> BaseAnswerSchema:
        raise NotImplementedError()


class EmptyResultHandler(AbstractHandler):
    async def process(self) -> BaseAnswerSchema | None:
        raise NextStepException("Сообщение не обработано")
