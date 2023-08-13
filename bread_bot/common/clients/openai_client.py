import logging
import random
from enum import StrEnum
from functools import lru_cache

import openai
from httpx import RequestError
from openai import OpenAIError
from pydantic import BaseModel

from bread_bot.main.settings.default import OPENAI_TOKEN, OPENAI_ORGANIZATION

logger = logging.getLogger()


class Role(StrEnum):
    USER = "user"
    SYSTEM = "system"
    BOT = "bot"


class ChatGptMessage(BaseModel):
    role: Role
    content: str


class ChatGptClient:
    def __init__(self):
        openai.organization = self.organization = OPENAI_ORGANIZATION
        openai.api_key = self.api_key = OPENAI_TOKEN

    async def get_chatgpt_answer(self, messages: list[ChatGptMessage]) -> ChatGptMessage:
        try:
            chat_completion = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                # TODO: Уверен, что можно настроить так, чтобы json.dumps() умел обрабатывать модели, но пока так
                messages=[message.dict() for message in messages],
                timeout=60,
            )
        except OpenAIError as e:
            logger.exception("ChatGPT service exception", exc_info=e)
            raise RequestError(e.args[0]) from e

        return ChatGptMessage(role=Role.BOT, content=random.choice(chat_completion.choices).message.content)


@lru_cache
def get_chat_gpt_client() -> ChatGptClient:
    return ChatGptClient()
