import os
from functools import lru_cache

from httpx import RequestError

from bread_bot.common.clients.openai_client import get_chat_gpt_client


class ThinkService:
    async def think_about(self, question: str) -> str:
        client = get_chat_gpt_client()
        try:
            result = await client.get_chatgpt_answer(
                await self.get_prompt(),
                question,
            )
            return result
        except RequestError:
            return "Не могу думать, думалка не работает((("

    @lru_cache
    async def get_prompt(self) -> str:
        # TODO: Нужна более гибкая система добавления промпта
        return os.getenv("MAIN_PROMPT", "Будь мудр и эпичен при ответе")
