import logging
import random
from enum import StrEnum
from functools import lru_cache

import openai
from httpx import RequestError
from openai import OpenAIError
from pydantic import BaseModel, Field

from bread_bot.main.settings.default import OPENAI_TOKEN, OPENAI_ORGANIZATION

logger = logging.getLogger()


class Role(StrEnum):
    USER = "user"
    SYSTEM = "system"
    BOT = "bot"


class ChatGptMessage(BaseModel):
    role: Role
    content: str


class DallEPicture(BaseModel):
    url: str


class DallEPrompt(BaseModel):
    prompt: str
    count_variants: int = Field(default=4, gt=0)
    height: int = Field(default=512, gt=0)
    length: int = Field(default=512, gt=0)

    @property
    def size(self) -> str:
        return f"{self.height}x{self.length}"


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

    async def get_dalle_image(self, prompt: DallEPrompt) -> list[DallEPicture]:
        try:
            response = await openai.Image.acreate(prompt=prompt.prompt, n=prompt.count_variants, size=prompt.size)
        except OpenAIError as e:
            logger.exception("Dall-E service exception")
            raise RequestError(e.args[0]) from e

        return [DallEPicture(url=image.url) for image in response.data]


@lru_cache
def get_chat_gpt_client() -> ChatGptClient:
    return ChatGptClient()
