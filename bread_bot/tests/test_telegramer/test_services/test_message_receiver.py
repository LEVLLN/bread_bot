import pytest

from bread_bot.telegramer.exceptions.base import RaiseUpException, NextStepException
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.services.handlers.command_handler import CommandHandler
from bread_bot.telegramer.services.handlers.handler import EmptyResultHandler
from bread_bot.telegramer.services.messages.message_receiver import MessageReceiver
from bread_bot.telegramer.services.messages.message_service import MessageService


@pytest.mark.parametrize(
    "exception, expected_return",
    [
        (Exception("some exception"), None),
        (NextStepException("some exception"), None),
        (
                RaiseUpException("some exception"),
                TextAnswerSchema(
                    text="some exception", chat_id=134,
                    reply_to_message_id=1,
                )
        ),
    ]
)
async def test_receive_fallback(db, mocker, message_service, exception, expected_return):
    message_receiver = MessageReceiver(db=db, request_body=message_service.request_body)
    mocker.patch.object(MessageService, "get_message", side_effect=exception)
    assert await message_receiver.receive() == expected_return


@pytest.mark.parametrize(
    "message_text, called_command_handler, called_empty_result_handler, expected",
    [
        (
                "Хлеб добавь подстроку",
                True,
                False,
                TextAnswerSchema(
                    text="Не найдено ключ-значения",
                    chat_id=134,
                    reply_to_message_id=1,
                ),
        ),
        (
                "Хлеб процент",
                True,
                False,
                TextAnswerSchema(
                    text="100",
                    reply_to_message_id=1,
                    chat_id=134,
                )
        ),
        ("Test", True, True, None),
        ("Хлеб", True, True, None),
    ],
)
async def test_receive_chain(
        db, mocker, message_service, message_text, called_command_handler, called_empty_result_handler, expected):
    command_result_handler_mock = mocker.spy(CommandHandler, "process")
    empty_result_handler_mock = mocker.spy(EmptyResultHandler, "process")
    message_service.message.text = message_text

    message_receiver = MessageReceiver(db=db, request_body=message_service.request_body)
    result = await message_receiver.receive()

    assert result == expected
    assert command_result_handler_mock.called is called_command_handler
    assert empty_result_handler_mock.called is called_empty_result_handler
