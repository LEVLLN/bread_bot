import random
import re

from bread_bot.telegramer.models import LocalMeme
from bread_bot.telegramer.services.processors.base_message_processor import MessageProcessor
from bread_bot.telegramer.utils.functions import composite_mask
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum, LocalMemeDataTypesEnum, TRIGGER_WORDS


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
        message_text_list = [message_text.replace(f"{trigger_word} ", "") for trigger_word in TRIGGER_WORDS]
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

    @staticmethod
    def _pack_data(local_meme: LocalMeme):
        result = {}
        for data_type in (LocalMemeDataTypesEnum.TEXT.value, LocalMemeDataTypesEnum.VOICE.value):
            if getattr(local_meme, data_type) is None:
                continue
            for key, value in getattr(local_meme, data_type).items():
                result[key] = (data_type, value)
        return result

    async def get_substring_words(self):
        """Обработка подстрок"""
        await self.count_stats(stats_enum=StatsEnum.CATCH_SUBSTRING)
        substring_words = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
        )
        if substring_words:
            data = self._pack_data(local_meme=substring_words)
        else:
            data = {}

        substring_words_mask = await composite_mask(
            collection=filter(lambda x: len(x) >= 3, sorted(data.keys(), key=len, reverse=True)),
            split=False,
        )
        regex = f'({substring_words_mask})'
        groups = re.findall(regex, self.message.text, re.IGNORECASE)

        if len(groups) > 0:
            substring_word = groups[0]
            data_type, value = data.get(substring_word.lower().strip(), "упс!")

            if isinstance(value, list):
                answer_value = random.choice(value)
            elif isinstance(value, str):
                answer_value = value
            else:
                answer_value = None

            match data_type:
                case LocalMemeDataTypesEnum.TEXT.value:
                    return await self.get_text_answer(answer_value)
                case LocalMemeDataTypesEnum.VOICE.value:
                    return await self.get_voice_answer(answer_value)
                case _:
                    return None

        return None
