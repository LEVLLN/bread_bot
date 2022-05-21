import logging

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.clients.telegram_client import TelegramClient
from bread_bot.telegramer.schemas.telegram_messages import StandardBodySchema
from bread_bot.telegramer.services.message_service import MessageService
from bread_bot.telegramer.services.processors import (
    AdminMessageProcessor,
    EditedMessageProcessor,
    MemberCommandMessageProcessor,
    PhrasesMessageProcessor,
    UtilsCommandMessageProcessor,
    VoiceMessageProcessor,

)

logger = logging.getLogger(__name__)


async def process_telegram_message(db: AsyncSession, request_body: StandardBodySchema):
    try:
        message_service = MessageService(db=db, request_body=request_body)
        if not await message_service.has_message and not await message_service.has_edited_message:
            return False
        await message_service.init()
    except Exception as e:
        logger.error("Error while handle message_service process", exc_info=e)
        return

    for Processor in [
        EditedMessageProcessor,
        VoiceMessageProcessor,
        AdminMessageProcessor,
        MemberCommandMessageProcessor,
        UtilsCommandMessageProcessor,
        PhrasesMessageProcessor,
    ]:
        result = await Processor(message_service=message_service).process()
        if result is not None:
            break

    if result is None:
        logger.error("Result answer schema is None: %s", request_body.dict())
        return

    try:
        await TelegramClient().send_message_by_schema(result)
    except Exception as e:
        logger.error("Error while sending message", exc_info=e)
