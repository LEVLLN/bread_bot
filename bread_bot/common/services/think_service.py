from httpx import RequestError

from bread_bot.common.clients.openai_client import get_chat_gpt_client


class ThinkService:
    async def _get_answer(self, full_query: str) -> str:
        client = get_chat_gpt_client()
        try:
            result = await client.get_chatgpt_answer(full_query)
        except RequestError:
            return "Ошибка работы получения ответа"
        else:
            return result

    async def think_about(self, question: str) -> str:
        return await self._get_answer(
            f"Расскажи, что ты думаешь про {question}. Уложись в три-четыре предложения. Расскажи об этом в "
            "юмористической и саркастической форме."
        )
