import logging

from fastapi import APIRouter
from starlette.requests import Request

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["root"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def root(request: Request):
    logger.info("Test log")
    return {"foo": "baz"}
