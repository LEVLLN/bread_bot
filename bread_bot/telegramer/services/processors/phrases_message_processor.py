import random
import re

from bread_bot.telegramer.models import LocalMeme
from bread_bot.telegramer.services.processors.base_message_processor import MessageProcessor
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.functions import composite_mask
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum


class PhrasesMessageProcessor(MessageProcessor):
    @property
    async def condition(self) -> bool:
        return random.random() < self.chat.answer_chance / 100

    async def _process(self):
        for method in [self.get_trigger_words, self.get_substring_words]:
            result = await method()
            if result is not None:
                return result
        return None

    async def get_trigger_words(self):
        """Обработка триггеров и привязок"""
        await self.count_stats(stats_enum=StatsEnum.CATCH_TRIGGER)
        trigger_words: LocalMeme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        if trigger_words is None:
            return None

        message_text = self.message.text.lower().strip()
        message_text_list = [message_text.replace(f"{trigger_word} ", "") for trigger_word in structs.TRIGGER_WORDS]
        message_text_list.append(message_text)

        result = None
        for message_text_candidate in message_text_list:
            if message_text_candidate in trigger_words.data:
                result = trigger_words.data.get(message_text_candidate, "упс!")
                break

        if isinstance(result, list):
            return await self.get_text_answer(answer_text=random.choice(result))
        elif isinstance(result, str):
            return await self.get_text_answer(answer_text=result)
        return None

    async def get_substring_words(self):
        """Обработка подстрок"""
        await self.count_stats(stats_enum=StatsEnum.CATCH_SUBSTRING)
        substring_words = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
        )
        substring_words = substring_words.data
        substring_words_mask = await composite_mask(
            collection=filter(lambda x: len(x) >= 3, substring_words.keys()),
            split=False,
        )
        regex = f'({substring_words_mask})'
        groups = re.findall(regex, self.message.text, re.IGNORECASE)

        if len(groups) > 0:
            substring_word = groups[0]
            value = substring_words.get(substring_word.lower().strip(), "упс!")

            if isinstance(value, list):
                return await self.get_text_answer(answer_text=random.choice(value))
            elif isinstance(value, str):
                return await self.get_text_answer(answer_text=value)
        return None
