from bread_bot.main.base_client import BaseHTTPClient
from bread_bot.common.schemas.api_models import EvilInsultResponse


class EvilInsultClient(BaseHTTPClient):
    def __init__(self):
        self.url = "https://evilinsult.com/generate_insult.php"

    async def get_evil_insult(self) -> EvilInsultResponse:
        response = await self.request(
            method="GET",
            url=self.url,
            query_params={
                "lang": "en",
                "type": "json",
            },
        )
        return EvilInsultResponse(**response.json())
