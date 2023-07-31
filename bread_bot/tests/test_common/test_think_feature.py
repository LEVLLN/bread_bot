from typing import Callable
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from bread_bot.common.async_tasks import async_free_promt, async_think_about
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


@pytest.fixture
def think_about_defer(mocker):
    return mocker.patch(
        "bread_bot.common.services.handlers.command_methods.entertainment_command_method.async_think_about.defer"
    )


@pytest.fixture
def free_promt_defer(mocker):
    return mocker.patch(
        "bread_bot.common.services.handlers.command_methods.entertainment_command_method.async_free_promt.defer"
    )


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


async def test_chat_gpt_excepted(db, chat_factory, message_factory, think_about_defer):
    message = f"{BOT_NAME} что думаешь про воду"
    body = message_factory(message)
    await chat_factory(chat_id=body.message.source.id, name="lol", is_openai_enabled=True)
    message_receiver = MessageReceiver(db=db, request_body=body)

    await message_receiver.receive()
    think_about_defer.assert_called_once()


async def test_what_you_think(db, chat_factory, message_factory, think_about_defer):
    message = f"{BOT_NAME} что думаешь про воду"
    body = message_factory(message)
    await chat_factory(chat_id=body.message.source.id, name="lol", is_openai_enabled=True)
    message_receiver = MessageReceiver(db=db, request_body=body)
    await message_receiver.receive()
    think_about_defer.assert_called_once_with(
        pre_promt="что думаешь про", text="воду", chat_id=body.message.source.id, reply_to_message_id=1
    )


async def test_what_you_think_task(mocker):
    spy = AsyncMock(return_value="Нормальный ответ на промт")
    mocker.patch(
        "bread_bot.common.services.think_service.get_chat_gpt_client",
        return_value=MagicMock(get_chatgpt_answer=spy),
    )
    send_mock = mocker.patch("bread_bot.common.clients.telegram_client.TelegramClient.send")
    await async_think_about(pre_promt="что думаешь про", text="LOL", chat_id=1, reply_to_message_id=1)
    send_mock.assert_called_once_with(
        **{
            "data": {"chat_id": 1, "reply_to_message_id": 1, "text": "Нормальный ответ на промт"},
            "method": "sendMessage",
        }
    )


async def test_free_promt(db, chat_factory, message_factory, free_promt_defer):
    message = f"{BOT_NAME} promt какой-то несложный промт"
    body = message_factory(message)
    await chat_factory(chat_id=body.message.source.id, name="lol", is_openai_enabled=True)
    message_receiver = MessageReceiver(db=db, request_body=body)
    await message_receiver.receive()
    free_promt_defer.assert_called_once_with(
        text="какой-то несложный промт",
        chat_id=body.message.source.id,
        reply_to_message_id=1,
    )


async def test_free_promt_task(mocker):
    spy = AsyncMock(return_value="Нормальный ответ на промт")
    mocker.patch(
        "bread_bot.common.services.think_service.get_chat_gpt_client",
        return_value=MagicMock(get_chatgpt_answer=spy),
    )
    send_mock = mocker.patch("bread_bot.common.clients.telegram_client.TelegramClient.send")
    await async_free_promt(text="LOL", chat_id=1, reply_to_message_id=1)
    send_mock.assert_called_once_with(
        **{
            "data": {"chat_id": 1, "reply_to_message_id": 1, "text": "Нормальный ответ на промт"},
            "method": "sendMessage",
        }
    )
