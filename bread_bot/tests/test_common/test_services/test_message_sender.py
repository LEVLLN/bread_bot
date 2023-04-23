import pytest

from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.services.messages.message_sender import MessageSender


@pytest.fixture()
def text_message():
    return TextAnswerSchema(
        reply_to_message_id=1,
        chat_id=1,
        text="some_text",
    )


@pytest.mark.parametrize(
    "text",
    (
        "some\n\nfooter",
        "some\n\n footer",
        "some\n\nfooter\n",
        "some\n\n footer\n",
        "some \n \n footer\n",
        "some \n\n \n\n footer\n",
        "some footer\n",
        "some text without new lines",
    ),
)
async def test_fit_messages(text_message, text):
    text_message.text = text
    result = MessageSender(message=text_message)._fit_in_messages()
    assert result[0].text == text
