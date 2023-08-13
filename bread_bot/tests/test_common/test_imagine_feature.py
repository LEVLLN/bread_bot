from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from bread_bot.common.async_tasks import async_imagine
from bread_bot.common.clients.openai_client import DallEPicture, DallEPrompt
from bread_bot.common.services.messages.message_receiver import MessageReceiver
from bread_bot.common.utils.structs import BOT_NAME


@pytest.fixture
def imagine_defer(mocker):
    return mocker.patch(
        "bread_bot.common.services.handlers.command_methods.entertainment_command_method.async_imagine.defer_async"
    )


async def test_imagine_is_available_only_for_openai_groups(db, message_factory):
    message = f"{BOT_NAME} представь что то прекрасное"
    body = message_factory(message)

    message_receiver = MessageReceiver(db=db, request_body=body)
    message = await message_receiver.receive()
    assert message.text == "Для данной группы функция недоступна."


async def test_imagine_called_async(db, message_factory, chat_factory, imagine_defer):
    message = f"{BOT_NAME} представь что то прекрасное"
    body = message_factory(message)
    await chat_factory(chat_id=body.message.source.id, name="lol", is_openai_enabled=True)

    message_receiver = MessageReceiver(db=db, request_body=body)
    await message_receiver.receive()

    imagine_defer.assert_called_once_with(
        **{"chat_id": 1, "count_variants": 1, "prompt": "что то прекрасное", "reply_to_message_id": 1}
    )


async def test_imagine_can_recieve_image_from_dalle(mocker: MockerFixture):
    spy = AsyncMock(return_value=[DallEPicture(url="https://google.com/image.png")])
    mocker.patch(
        "bread_bot.common.services.think_service.get_chat_gpt_client",
        return_value=MagicMock(get_dalle_image=spy),
    )
    send_mock = mocker.patch("bread_bot.common.clients.telegram_client.TelegramClient.send")

    await async_imagine(1, 1, "что то прекрасное", 1)

    send_mock.assert_called_once_with(
        **{
            "data": {
                "caption": "что то прекрасное (c) Хлеб",
                "chat_id": 1,
                "photo": "https://google.com/image.png",
                "reply_to_message_id": 1,
            },
            "method": "sendPhoto",
        }
    )
    spy.assert_called_once_with(
        prompt=DallEPrompt(prompt="что то прекрасное", count_variants=1, height=512, length=512)
    )
