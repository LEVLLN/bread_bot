import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from bread_bot.telegramer.models import LocalMeme
from bread_bot.telegramer.schemas.local_memes import LocalMemeSchema
from bread_bot.telegramer.schemas.telegram_messages import StandardBodySchema
from bread_bot.telegramer.services.message_handler import MessageHandler
from bread_bot.utils.dependencies import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=['telegram'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/')
async def handle_message(
        request: Request,
        request_body: StandardBodySchema,
        db: AsyncSession = Depends(get_async_session)
):
    import json
    data = await request.body()
    logger.debug(json.loads(data))
    try:
        await MessageHandler(request_body=request_body, db=db).handle_message()
    except Exception:
        pass
    return 'OK'


@router.post('/set_local_meme')
async def set_local_meme(
        request_body: LocalMemeSchema,
        db: AsyncSession = Depends(get_async_session)
):

    local_meme = await LocalMeme.async_first(
        session=db,
        filter_expression=(LocalMeme.type == request_body.type) &
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
