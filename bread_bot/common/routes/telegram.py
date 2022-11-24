import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse
import markdown

from bread_bot.auth.methods.auth_methods import get_current_active_admin_user
from bread_bot.common.clients.telegram_client import TelegramClient
from bread_bot.common.models import Chat, Member
from bread_bot.common.schemas.api_models import SendMessageSchema, ChatSchema, MemberDBSchema
from bread_bot.common.schemas.telegram_messages import \
    StandardBodySchema, \
    ChatMemberBodySchema
from bread_bot.common.services.messages.message_receiver import MessageReceiver
from bread_bot.common.services.messages.message_sender import MessageSender
from bread_bot.utils.dependencies import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=['telegram'],
    responses={404: {'description': 'Not found'}},
)

RESPONSE_OK = "OK"


@router.post("/")
async def handle_message(
        request_body: StandardBodySchema,
        db: AsyncSession = Depends(get_async_session)
):
    message_receiver = MessageReceiver(db=db, request_body=request_body)
    message = await message_receiver.receive()
    if not message:
        return RESPONSE_OK
    message_sender = MessageSender(message=message)
    await message_sender.send_messages_to_chat()
    return RESPONSE_OK


@router.get("/help", response_class=HTMLResponse)
async def color_home(request: Request):
    with open("./About.md", "r", encoding="utf-8") as input_file:
        text = input_file.read()
    return markdown.markdown(text)


@router.post('/send_message',
             dependencies=[Depends(get_current_active_admin_user)])
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Произошла ошибка отправки сообщения'
        )
    return RESPONSE_OK


@router.get('/chats',
            response_model=List[ChatSchema],
            dependencies=[Depends(get_current_active_admin_user)])
async def get_chats(db: AsyncSession = Depends(get_async_session)):
    return await Chat.async_filter(db, where=Chat.chat_id < 0)


@router.get('/members',
            response_model=List[MemberDBSchema],
            dependencies=[Depends(get_current_active_admin_user)])
async def get_members(db: AsyncSession = Depends(get_async_session)):
    return await Member.async_all(db)


@router.get('/members/{object_id}',
            response_model=MemberDBSchema,
            dependencies=[Depends(get_current_active_admin_user)])
async def get_member_by_id(
        object_id: int,
        db: AsyncSession = Depends(get_async_session)):
    member = await Member.async_first(db, Member.id == object_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден'
        )
    return member


@router.delete(
    '/members/{object_id}',
    dependencies=[Depends(get_current_active_admin_user)])
async def delete_members(
        object_id: int,
        db: AsyncSession = Depends(get_async_session)):
    return {
        'deleted': await Member.async_delete(
            db=db,
            where=Member.id == object_id)
    }


@router.get('/admins_of_chat/{chat_id}',
            response_model=ChatMemberBodySchema,
            dependencies=[Depends(get_current_active_admin_user)])
async def admins_of_chat(
        chat_id: int,
):
    try:
        return await TelegramClient().get_chat(chat_id=chat_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
