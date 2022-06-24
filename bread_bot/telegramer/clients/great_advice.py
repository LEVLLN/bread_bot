import logging
from urllib.parse import urljoin

from bread_bot.main.base_client import BaseHTTPClient
from bread_bot.telegramer.schemas.api_models import GreatAdviceResponse

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
