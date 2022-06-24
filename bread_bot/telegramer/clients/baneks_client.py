import logging
import random
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from bread_bot.main.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class BaneksClient(BaseHTTPClient):
    def __init__(self):
        self.url = "https://baneks.ru"
        self.random_method = str(random.randint(1, 1142))

    @property
    async def random_url(self) -> str:
        return urljoin(self.url, self.random_method)

    async def get_quote(self) -> str:
        response = await self.request(
            method="GET",
            url=await self.random_url,
            headers={
                'Accept': '*/*',
            }
        )
        return response.text

    async def get_text(self) -> Optional[str]:
        try:
            html = await self.get_quote()
            text = BeautifulSoup(html, "html.parser") \
                .find(name="article",).find("p").get_text()
        except Exception as e:
            logger.error(str(e))
            return None
        else:
            return text
