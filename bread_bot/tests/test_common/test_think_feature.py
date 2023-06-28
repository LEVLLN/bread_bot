from typing import Callable
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from bread_bot.common.schemas.telegram_messages import (
    StandardBodySchema,
    MessageSchema,
    MemberSchema,
    ChatSchema,
)
from bread_bot.common.services.messages.message_receiver import MessageReceiver
from bread_bot.common.utils.structs import BOT_NAME
from bread_bot.main.webserver import app

client = TestClient(app)


@pytest.fixture
def message_factory() -> Callable:
    def wrap(message_text: str = "") -> StandardBodySchema:
        return StandardBodySchema(
            update_id=1,
            message=MessageSchema(
                message_id=1,
                source=MemberSchema(id=1, is_bot=False),
                chat=ChatSchema(id=1),
                text=message_text,
            ),
            edited_message=None,
        )

    return wrap


async def test_can_handle_message(message_factory):
    body = message_factory().dict()
    response = client.post(
        "/",
        json=body,
    )

    assert response.status_code == 200
    assert response.json() == "OK"


async def test_what_you_think_is_available(db, message_factory):
    message = f"{BOT_NAME} что думаешь про воду"
    body = message_factory(message)

    message_receiver = MessageReceiver(db=db, request_body=body)
    message = await message_receiver.receive()

    assert message is not None


async def test_chat_gpt_excepted(db, message_factory):
    message = f"{BOT_NAME} что думаешь про воду"
    body = message_factory(message)
    message_receiver = MessageReceiver(db=db, request_body=body)

    result = await message_receiver.receive()

    assert result.text == "Не могу думать, думалка не работает((("


async def test_what_you_think(db, message_factory, mocker: MockerFixture):
    message = f"{BOT_NAME} что думаешь про воду"
    body = message_factory(message)
    message_receiver = MessageReceiver(db=db, request_body=body)

    spy = AsyncMock(return_value="Вода чертовски хороша!")
    mocker.patch(
        "bread_bot.common.services.think_service.get_chat_gpt_client",
        return_value=MagicMock(get_chatgpt_answer=spy),
    )
    result = await message_receiver.receive()

    assert result.text == "Вода чертовски хороша!"
    spy.assert_called_once_with("Будь мудр и эпичен при ответе", "что думаешь про воду")
