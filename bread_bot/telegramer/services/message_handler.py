import logging
import random
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.schemas.telegram_messages import \
    StandardBodySchema, MessageSchema
from bread_bot.telegramer.services.bread_service_handler import \
    BreadServiceHandler
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.utils import structs

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(
            self,
            request_body: StandardBodySchema = None,
            db: AsyncSession = None
    ):
        self.request_body = request_body
        self.has_message = \
            hasattr(self.request_body, 'message') \
            and self.request_body.message is not None
        self.has_edited_message = \
            hasattr(self.request_body, 'edited_message') \
            and self.request_body.edited_message is not None
        self.message: Optional[MessageSchema] = \
            self.request_body.edited_message \
            if self.has_edited_message else self.request_body.message
        self.client = TelegramClient()
        self.db = db

    async def validate_command(self):
        if not self.has_message and not self.has_edited_message:
            return False
        return True

    async def handle_message(self):
        if not await self.validate_command():
            return
        bread_service = BreadServiceHandler(
            client=self.client,
            message=self.message,
            db=self.db,
            is_edited=self.has_edited_message,
        )
        try:
            result_text = await bread_service.build_message()
        except Exception as e:
            logger.error(str(e))
            await self.client.send_message(
                chat_id=self.message.chat.id,
                message=random.choice(structs.ERROR_CHAT_MESSAGES),
                reply_to=self.message.message_id,
            )
            raise e
        else:
            if result_text is None:
                return
            await self.client.send_message(
                chat_id=self.message.chat.id,
                message=result_text,
                reply_to=self.message.message_id
                if bread_service.reply_to_message else None,
            )
