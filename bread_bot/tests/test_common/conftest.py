from typing import Callable

import pytest

from bread_bot.common.schemas.telegram_messages import StandardBodySchema, MessageSchema, MemberSchema, ChatSchema


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
