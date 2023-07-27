import logging
from functools import lru_cache

import openai
from httpx import RequestError
from openai import OpenAIError

from bread_bot.main.settings.default import OPENAI_TOKEN, OPENAI_ORGANIZATION

logger = logging.getLogger()


class ChatGptClient:
    def __init__(self):
        openai.organization = self.organization = OPENAI_ORGANIZATION
        openai.api_key = self.api_key = OPENAI_TOKEN

    async def get_chatgpt_answer(self, query: str) -> str:
        try:
            chat_completion = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                timeout=5 * 360,
            )
        except OpenAIError as e:
            logger.exception("ChatGPT service exception", exc_info=e)
            raise RequestError(e.args[0]) from e

        return chat_completion.choices[0].message.content


@lru_cache
def get_chat_gpt_client() -> ChatGptClient:
    return ChatGptClient()
