from httpx import RequestError

from bread_bot.common.clients.openai_client import get_chat_gpt_client


class OpenAIService:
    async def _get_answer(self, full_query: str) -> str:
        client = get_chat_gpt_client()
        try:
            result = await client.get_chatgpt_answer(full_query)
        except RequestError:
            return "Ошибка работы получения ответа"
        else:
            return result

    async def think_about(self, pre_promt: str, question: str) -> str:
        return await self._get_answer(
            f"{pre_promt} {question}. Уложись в три-четыре предложения. Расскажи об этом в "
            "юмористической и саркастической форме."
        )

    async def free_promt(self, question: str) -> str:
        return await self._get_answer(question)
