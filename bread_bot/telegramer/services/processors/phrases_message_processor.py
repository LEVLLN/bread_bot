import logging
import random
import re

from bread_bot.telegramer.models import LocalMeme
from bread_bot.telegramer.services.processors.base_message_processor import MessageProcessor
from bread_bot.telegramer.utils.functions import composite_mask
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum, LocalMemeDataTypesEnum, TRIGGER_WORDS

logger = logging.getLogger(__name__)


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
        await self.count_stats(stats_enum=StatsEnum.CATCH_TRIGGER)
        if isinstance(result, list):
            return await self.get_text_answer(answer_text=random.choice(result))
        elif isinstance(result, str):
            return await self.get_text_answer(answer_text=result)
        return None

    async def get_substring_words(self):
        """Обработка подстрок"""
        substring_words = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
        )
        if substring_words is None:
            logger.warning("Substrings object not found", extra={
                "chat_id": self.chat.chat_id,
            })
            return None

        data_to_choice_list = []
        for data_type in (LocalMemeDataTypesEnum.TEXT.value,
                          LocalMemeDataTypesEnum.VOICE.value,
                          LocalMemeDataTypesEnum.PHOTO.value,
                          LocalMemeDataTypesEnum.STICKER.value):
            data = getattr(substring_words, data_type)
            if data is None:
                continue
            substring_words_mask = await composite_mask(
                collection=filter(lambda x: len(x) >= 3, sorted(data.keys(), key=len, reverse=True)),
                split=False,
            )
            regex = f'({substring_words_mask})'
            groups = re.findall(regex, self.message.text, re.IGNORECASE)

            if len(groups) == 0:
                continue
            substring_word = groups[0]
            data_to_choice_list.append((data_type, data.get(substring_word.lower().strip(), "упс!")))

        if not data_to_choice_list:
            logger.warning("Substrings object not found", extra={
                "chat_id": self.chat.chat_id,
            })
            return None

        data_type, value = random.choice(data_to_choice_list)

        if isinstance(value, list):
            answer_value = random.choice(value)
        elif isinstance(value, str):
            answer_value = value
        else:
            logger.warning("Unavailable value type, for substring", extra={
                "chat_id": self.chat.chat_id,
                "value": value,
                "type": type(value),
            })
            return None

        await self.count_stats(stats_enum=StatsEnum.CATCH_SUBSTRING)
        match data_type:
            case LocalMemeDataTypesEnum.TEXT.value:
                return await self.get_text_answer(answer_value)
            case LocalMemeDataTypesEnum.VOICE.value:
                return await self.get_voice_answer(answer_value)
            case LocalMemeDataTypesEnum.PHOTO.value:
                return await self.get_photo_answer(answer_value)
            case LocalMemeDataTypesEnum.STICKER.value:
                return await self.get_sticker_answer(answer_value)
            case _:
                logger.warning("Data type of substring undefined", extra={
                    "chat_id": self.chat.chat_id,
                    "data_type": data_type,
                })
                return None
