import pytest
from sqlalchemy import and_

from bread_bot.telegramer.models import Stats, Chat
from bread_bot.telegramer.schemas.bread_bot_answers import VoiceAnswerSchema
from bread_bot.telegramer.services.processors import EditedMessageProcessor, VoiceMessageProcessor
from bread_bot.telegramer.utils.structs import StatsEnum, PropertiesEnum


class TestVoiceMessageProcessor:
    async def test_not_voice_message(self, db, edited_message_service):
        processor = EditedMessageProcessor(message_service=edited_message_service)
        assert await processor.process() is None
        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.VOICER.name)) is None

    @pytest.mark.parametrize(
        "slug, data, chat_is_voice_trigger, expected_result",
        [
            (
                    PropertiesEnum.BAD_VOICES.name,
                    ["some_answer_voice"],
                    True,
                    VoiceAnswerSchema(reply_to_message_id=1, voice_file_id="some_answer_voice", chat_id=134),
            ),
            (
                    PropertiesEnum.BAD_VOICES.name,
                    [],
                    True,
                    None,
            ),
            (
                    PropertiesEnum.ANSWER_TO_EDIT.name,
                    ["some"],
                    True,
                    None,
            ),
            (
                    PropertiesEnum.BAD_VOICES.name,
                    ["some"],
                    False,
                    None,
            ),
        ]
    )
    async def test_process_message(self, db, voice_message_service, property_factory,
                                   slug, chat_is_voice_trigger, data, expected_result):
        await property_factory(slug=slug, data=data)
        chat = voice_message_service.chat
        chat.is_voice_trigger = chat_is_voice_trigger
        await Chat.async_add(db=db, instance=chat)

        processor = VoiceMessageProcessor(message_service=voice_message_service)
        assert await processor.process() == expected_result

        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.VOICER.name)) is not None
