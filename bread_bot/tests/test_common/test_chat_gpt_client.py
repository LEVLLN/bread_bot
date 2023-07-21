import pytest
from httpx import RequestError

from bread_bot.common.clients.openai_client import get_chat_gpt_client


def test_chat_gpt_client_factory():
    from bread_bot.common.clients.openai_client import (
        get_chat_gpt_client,
        ChatGptClient,
    )

    client = get_chat_gpt_client()

    assert isinstance(client, ChatGptClient)
    assert (client.api_key, client.organization) == (None, None)


async def test_get_chatgpt_answer_without_credentilas():
    client = get_chat_gpt_client()

    with pytest.raises(RequestError) as t:
        await client.get_chatgpt_answer("")

    assert t.match("No API key provided")
