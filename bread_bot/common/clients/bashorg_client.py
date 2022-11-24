import logging
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from bread_bot.main.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class BashOrgClient(BaseHTTPClient):
    def __init__(self):
        self.url = "http://bashorg.org"
        self.casual_method = "casual"

    @property
    def casual_url(self) -> str:
        return urljoin(self.url, self.casual_method)

    async def get_quote(self) -> str:
        response = await self.request(
            method="GET",
            url=self.casual_url,
            headers={
                'Accept': '*/*',
            }
        )
        return response.text

    async def get_text(self) -> Optional[str]:
        try:
            html = await self.get_quote()
            text = BeautifulSoup(html, "html.parser") \
                .find(name="div", recursive=True, id="quotes") \
                .div \
                .find("div", **{"class": None}) \
                .get_text(separator="\n")
        except Exception as e:
            logger.error(str(e))
            return None
        return text
