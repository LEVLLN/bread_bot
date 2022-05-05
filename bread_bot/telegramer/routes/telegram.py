import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from bread_bot.auth.methods.auth_methods import get_current_active_admin_user
from bread_bot.telegramer.models import LocalMeme, Chat, Member
from bread_bot.telegramer.schemas.api_models import LocalMemeSchema, \
    SendMessageSchema, ChatSchema, MemberDBSchema
from bread_bot.telegramer.schemas.telegram_messages import \
    StandardBodySchema, \
    ChatMemberBodySchema
from bread_bot.telegramer.services.message_handler import MessageHandler
from bread_bot.telegramer.clients.telegram_client import TelegramClient
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum
from bread_bot.utils.dependencies import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=['telegram'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/')
async def handle_message(
        request_body: StandardBodySchema,
        db: AsyncSession = Depends(get_async_session)
):
    try:
        await MessageHandler(request_body=request_body, db=db).handle_message()
    except Exception:
        pass
    return 'OK'


@router.post('/set_local_meme',
             dependencies=[Depends(get_current_active_admin_user)])
async def set_local_meme(
        request_body: LocalMemeSchema,
        db: AsyncSession = Depends(get_async_session)
):
    local_meme = await LocalMeme.async_first(
        db=db,
        where=(LocalMeme.type == request_body.type) &
              (LocalMeme.chat_id == request_body.chat_id),
    )
    if not local_meme:
        await LocalMeme.async_add_by_schema(
            db=db,
            instance_schema=request_body,
        )
    else:
        local_meme.data = request_body.data
        await LocalMeme.async_add(db, local_meme)
    return 'OK'


@router.get('/get_local_memes/{chat_id}',
            dependencies=[Depends(get_current_active_admin_user)],
            response_model=List[LocalMemeSchema]
            )
async def get_local_meme(
        chat_id: int,
        meme_type: Optional[str] = None,
        db: AsyncSession = Depends(get_async_session)
):
    condition = [LocalMeme.chat_id == chat_id, ]
    if meme_type is not None \
            and getattr(LocalMemeTypesEnum, meme_type, None):
        condition.append(LocalMeme.type == meme_type)

    local_memes = await LocalMeme.async_filter(
        db=db,
        where=and_(*condition)
    )
    if not local_memes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено данных'
        )
    return local_memes


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
    return 'OK'


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
