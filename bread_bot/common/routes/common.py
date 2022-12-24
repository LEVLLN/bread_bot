import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from bread_bot.auth.methods.auth_methods import get_current_active_admin_user
from bread_bot.common.clients.telegram_client import TelegramClient
from bread_bot.common.models import Chat
from bread_bot.common.schemas.api_models import SendMessageSchema, ChatSchema, ReleaseNotesSchema
from bread_bot.common.schemas.telegram_messages import StandardBodySchema, ChatMemberBodySchema
from bread_bot.common.services.messages.message_receiver import MessageReceiver
from bread_bot.common.services.messages.message_sender import MessageSender
from bread_bot.utils.dependencies import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["common"],
    responses={404: {"description": "Not found"}},
)

RESPONSE_OK = "OK"


@router.post("/")
async def handle_message(request_body: StandardBodySchema, db: AsyncSession = Depends(get_async_session)):
    message_receiver = MessageReceiver(db=db, request_body=request_body)
    message = await message_receiver.receive()

    message_sender = MessageSender(message=message)
    await message_sender.send_messages_to_chat()
    return RESPONSE_OK


@router.post("/send_message", dependencies=[Depends(get_current_active_admin_user)])
async def send_message_to_chat(
    message: SendMessageSchema,
):
    telegram_client = TelegramClient()
    try:
        await telegram_client.send_message(
            chat_id=message.chat_id,
            message=message.message,
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Произошла ошибка отправки сообщения")
    return RESPONSE_OK


@router.get("/chats", response_model=List[ChatSchema], dependencies=[Depends(get_current_active_admin_user)])
async def get_chats(db: AsyncSession = Depends(get_async_session)):
    return await Chat.async_filter(db, where=Chat.chat_id < 0)


@router.get(
    "/admins_of_chat/{chat_id}",
    response_model=ChatMemberBodySchema,
    dependencies=[Depends(get_current_active_admin_user)],
)
async def admins_of_chat(
    chat_id: int,
):
    try:
        return await TelegramClient().get_chat(chat_id=chat_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/release_notes", dependencies=[Depends(get_current_active_admin_user)])
async def release_notes(message: ReleaseNotesSchema, db: AsyncSession = Depends(get_async_session)):
    chats = await Chat.async_filter(db, where=Chat.chat_id < 0)
    telegram_client = TelegramClient()
    for chat in chats:
        try:
            await telegram_client.send_message(
                chat_id=chat.chat_id,
                message=message.message,
            )
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Произошла ошибка отправки сообщения")
    return RESPONSE_OK
