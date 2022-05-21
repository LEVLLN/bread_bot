import pytest
from sqlalchemy import and_

from bread_bot.telegramer.models import Stats, Chat
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.services.processors import EditedMessageProcessor
from bread_bot.telegramer.utils.structs import StatsEnum, PropertiesEnum


class TestEditedMessageProcessor:
    async def test_is_not_edited_message(self, db, message_service):
        processor = EditedMessageProcessor(message_service=message_service)
        assert await processor.process() is None
        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.EDITOR.name)) is None

    @pytest.mark.parametrize(
        "slug, data, chat_is_edited_trigger, expected_result",
        [
            (
                    PropertiesEnum.ANSWER_TO_EDIT.name,
                    ["some"],
                    True,
                    TextAnswerSchema(reply_to_message_id=1, text="some", chat_id=134),
            ),
            (
                    PropertiesEnum.ANSWER_TO_EDIT.name,
                    [],
                    True,
                    None,
            ),
            (
                    PropertiesEnum.BAD_VOICES.name,
                    ["some"],
                    True,
                    None,
            ),
            (
                    PropertiesEnum.ANSWER_TO_EDIT.name,
                    ["some"],
                    False,
                    None,
            ),
        ]
    )
    async def test_edited_message(self, db, edited_message_service, property_factory,
                                  slug, data, chat_is_edited_trigger, expected_result):
        await property_factory(slug=slug, data=data)
        chat = edited_message_service.chat
        chat.is_edited_trigger = chat_is_edited_trigger
        await Chat.async_add(db=db, instance=chat)

        processor = EditedMessageProcessor(message_service=edited_message_service)
        assert await processor.process() == expected_result

        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.EDITOR.name)) is not None
