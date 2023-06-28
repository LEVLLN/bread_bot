from httpx import RequestError

from bread_bot.common.clients.openai_client import get_chat_gpt_client


class ThinkService:
    async def think_about(self, question: str) -> str:
        client = get_chat_gpt_client()
        try:
            result = await client.get_chatgpt_answer(
                "Будь мудр и эпичен при ответе",
                question,
            )
            return result
        except RequestError:
            return "Не могу думать, думалка не работает((("
