import random
from typing import Optional

from bread_bot.telegramer.models import Property
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.services.processors.base_message_processor import MessageProcessor
from bread_bot.telegramer.utils.structs import StatsEnum, PropertiesEnum


class EditedMessageProcessor(MessageProcessor):
    @property
    async def condition(self) -> bool:
        return await self.message_service.has_edited_message

    async def _process(self) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.EDITOR)
        if not self.chat.is_edited_trigger:
            return None

        editor_messages: Property = await Property.async_first(
            db=self.db,
            where=Property.slug == PropertiesEnum.ANSWER_TO_EDIT.name,
        )
        if editor_messages is None or not editor_messages.data:
            return None

        return await self.get_text_answer(
            answer_text=random.choice(editor_messages.data)
        )
