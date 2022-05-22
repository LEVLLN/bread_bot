from urllib.parse import urljoin

from bread_bot.main.base_client import BaseHTTPClient


class BashOrgClient(BaseHTTPClient):
    def __init__(self):
        self.url = "http://bashorg.org"
        self.casual_method = "casual"

    @property
    async def casual_url(self) -> str:
        return urljoin(self.url, self.casual_method)

    async def get_quote(self) -> str:
        response = await self.request(
            method="GET",
            url="http://bashorg.org/casual",
            headers={
                'Accept': '*/*',
            }
        )
        return response.text
