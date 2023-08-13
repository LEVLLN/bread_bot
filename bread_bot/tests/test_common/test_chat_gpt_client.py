import json

import pytest
from httpx import RequestError

from bread_bot.common.clients.openai_client import get_chat_gpt_client, ChatGptMessage, Role


def test_model_as_json():
    assert json.dumps(Role.SYSTEM) == '"system"'
    message = ChatGptMessage(role=Role.SYSTEM, content="Some")
    assert json.dumps(message) == '{"role": "system", "content": "Some"}'


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
        await client.get_chatgpt_answer([ChatGptMessage(role=Role.USER, content="")])

    assert t.match("No API key provided")
