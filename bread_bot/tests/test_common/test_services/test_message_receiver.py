import pytest

from bread_bot.common.exceptions.base import RaiseUpException, NextStepException
from bread_bot.common.models import AnswerPack, AnswerPacksToChats
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.services.handlers.answer_handler import TriggerAnswerHandler, SubstringAnswerHandler
from bread_bot.common.services.handlers.command_handler import CommandHandler
from bread_bot.common.services.handlers.handler import EmptyResultHandler
from bread_bot.common.services.messages.message_receiver import MessageReceiver
from bread_bot.common.services.messages.message_service import MessageService
from bread_bot.common.utils.structs import AnswerEntityReactionTypesEnum


@pytest.fixture
async def based_pack(db, member_service):
    answer_pack = await AnswerPack.async_add(db, instance=AnswerPack())
    await AnswerPacksToChats.async_add(
        db=db,
        instance=AnswerPacksToChats(
            chat_id=member_service.chat.id,
            pack_id=answer_pack.id,
        ),
    )
    yield answer_pack


@pytest.mark.parametrize(
    "exception, expected_return",
    [
        (Exception("some exception"), None),
        (NextStepException("some exception"), None),
        (
            RaiseUpException("some exception"),
            TextAnswerSchema(
                text="some exception",
                chat_id=134,
                reply_to_message_id=1,
            ),
        ),
    ],
)
async def test_receive_fallback(db, mocker, message_service, exception, expected_return):
    message_receiver = MessageReceiver(db=db, request_body=message_service.request_body)
    mocker.patch.object(MessageService, "get_message", side_effect=exception)
    assert await message_receiver.receive() == expected_return


@pytest.mark.parametrize(
    "message_text, called_command_handler, called_trigger_handler, "
    "called_substring_handler, called_empty_result_handler, expected",
    [
        (
            "Хлеб добавь подстроку",
            True,
            False,
            False,
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
            False,
            False,
            TextAnswerSchema(
                text="100",
                reply_to_message_id=1,
                chat_id=134,
            ),
        ),
        (
            "I called my_substring_key",
            True,
            True,
            True,
            False,
            TextAnswerSchema(
                text="some_value_substring",
                chat_id=134,
                reply_to_message_id=1,
            ),
        ),
        (
            "my_trigger_key",
            True,
            True,
            False,
            False,
            TextAnswerSchema(
                text="some_value_trigger",
                chat_id=134,
                reply_to_message_id=1,
            ),
        ),
        ("Test", True, True, True, True, None),
        ("Хлеб", True, True, True, True, None),
    ],
)
async def test_receive_chain(
    db,
    mocker,
    message_service,
    message_text,
    based_pack,
    called_command_handler,
    called_empty_result_handler,
    called_trigger_handler,
    called_substring_handler,
    text_entity_factory,
    expected,
):
    await text_entity_factory(
        key="my_substring_key",
        value="some_value_substring",
        reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING,
        pack_id=based_pack.id,
    )
    await text_entity_factory(
        key="my_trigger_key",
        value="some_value_trigger",
        reaction_type=AnswerEntityReactionTypesEnum.TRIGGER,
        pack_id=based_pack.id,
    )
    command_result_handler_mock = mocker.spy(CommandHandler, "process")
    trigger_answer_handler_mock = mocker.spy(TriggerAnswerHandler, "process")
    substring_answer_handler_mock = mocker.spy(SubstringAnswerHandler, "process")
    empty_result_handler_mock = mocker.spy(EmptyResultHandler, "process")
    message_service.message.text = message_text

    message_receiver = MessageReceiver(db=db, request_body=message_service.request_body)
    result = await message_receiver.receive()

    assert result == expected
    assert command_result_handler_mock.called is called_command_handler
    assert empty_result_handler_mock.called is called_empty_result_handler
    assert trigger_answer_handler_mock.called is called_trigger_handler
    assert substring_answer_handler_mock.called is called_substring_handler
