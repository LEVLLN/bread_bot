from httpx import RequestError

from bread_bot.common.clients.openai_client import get_chat_gpt_client, Role, ChatGptMessage


class OpenAIService:
    async def _get_answer(self, messages: list[ChatGptMessage]) -> ChatGptMessage:
        client = get_chat_gpt_client()
        try:
            result = await client.get_chatgpt_answer(messages)
        except RequestError:
            return ChatGptMessage(role=Role.SYSTEM, content="Ошибка работы получения ответа")
        else:
            return result

    async def think_about(self, pre_promt: str, question: str) -> str:
        messages = [
            ChatGptMessage(role=Role.SYSTEM, content=pre_promt),
            ChatGptMessage(
                role=Role.SYSTEM,
                content="Уложись в три-четыре предложения. Расскажи об этом в юмористической и саркастической форме.",
            ),
            ChatGptMessage(role=Role.USER, content=question),
        ]
        answer = await self._get_answer(messages)
        return answer.content

    async def free_prompt(self, question: str) -> str:
        answer = await self._get_answer([ChatGptMessage(role=Role.USER, content=question)])
        return answer.content
