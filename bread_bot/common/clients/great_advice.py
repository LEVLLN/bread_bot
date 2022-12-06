import logging

from bread_bot.common.schemas.api_models import GreatAdviceResponse
from bread_bot.main.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class GreatAdviceClient(BaseHTTPClient):
    def __init__(self):
        self.url = "http://fucking-great-advice.ru/api/random"

    async def get_advice(self) -> GreatAdviceResponse:
        response = await self.request(
            method="GET",
            url=self.url,
        )
        return GreatAdviceResponse(**response.json())
