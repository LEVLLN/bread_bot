from bread_bot.main.base_client import BaseHTTPClient
from bread_bot.common.schemas.api_models import ForismaticQuote


class ForismaticClient(BaseHTTPClient):
    def __init__(self):
        self.url = 'http://api.forismatic.com/api/1.0/'

    async def get_quote_text(self) -> ForismaticQuote:
        response = await self.request(
            method='GET',
            url=self.url,
            query_params={
                'method': 'getQuote',
                'key': 0,
                'format': 'json',
                'lang': 'ru'
            }
        )
        return ForismaticQuote(**response.json())
