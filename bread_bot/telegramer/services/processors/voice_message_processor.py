import random
from typing import Optional

from bread_bot.telegramer.models import Property
from bread_bot.telegramer.schemas.bread_bot_answers import VoiceAnswerSchema
from bread_bot.telegramer.services.processors.base_message_processor import MessageProcessor
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import StatsEnum


class VoiceMessageProcessor(MessageProcessor):
    @property
    async def condition(self) -> bool:
        return self.message.voice is not None \
               and self.message.voice.duration \
               and self.message.voice.duration >= 1

    async def _process(self) -> Optional[VoiceAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.VOICER)

        if not self.chat.is_voice_trigger:
            return None

        condition = Property.slug == structs.PropertiesEnum.BAD_VOICES.name
        voice_list: Property = await Property.async_first(
            db=self.db,
            where=condition,
        )

        if not voice_list or not voice_list.data:
            return None

        return VoiceAnswerSchema(
            voice=random.choice(voice_list.data),
            chat_id=self.chat.chat_id,
            reply_to_message_id=self.message.message_id,
        )
