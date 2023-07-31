import logging

from fastapi import APIRouter
from starlette.requests import Request

from bread_bot.common.async_tasks import async_free_promt
from bread_bot.main.procrastinate import app

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["root"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def root(request: Request):
    async with app.open_async():
        await async_free_promt.defer_async(text="LOL", chat_id=1, reply_to_message_id=1)
    logger.info("Test log")
    return {"foo": "baz"}
