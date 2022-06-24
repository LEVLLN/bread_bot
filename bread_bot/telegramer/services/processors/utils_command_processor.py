import logging
import random
from typing import Optional

from bread_bot.telegramer.clients.bashorg_client import BashOrgClient
from bread_bot.telegramer.clients.evil_insult_client import EvilInsultClient
from bread_bot.telegramer.clients.forismatic_client import ForismaticClient
from bread_bot.telegramer.clients.great_advice import GreatAdviceClient
from bread_bot.telegramer.models import Property
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema, VoiceAnswerSchema
from bread_bot.telegramer.services.processors.base_command_processor import CommandMessageProcessor
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum, PropertiesEnum

logger = logging.getLogger(__name__)


class UtilsCommandMessageProcessor(CommandMessageProcessor):
    METHODS_MAP = {
        "оскорби": "handle_rude_words",
        "цифри": "get_num",
        "цифры": "get_num",
        "рандом": "get_num",
        "шанс": "get_chance",
        "вероятность": "get_chance",
        "help": "help",
        "hlep": "help",
        "хелп": "help",
        "выбери": "choose_variant",
        "цитата": "get_quote",
        "цит": "get_quote",
        "insult": "get_insult",
        "анекдот": "get_joke",
        "совет": "get_great_advice",
    }

    async def handle_rude_words(self) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.INSULTER)
        username = None
        if self.message.reply:
            username = f'@{self.message.reply.source.username}'
        rude_messages = await self.get_list_messages(
            meme_type=LocalMemeTypesEnum.RUDE_WORDS.name)
        if not rude_messages:
            return await self.get_text_answer(answer_text="Необходимо пополнить базу "
                                                          "через команду 'добавь оскорбление ключ=значение'")
        if username is not None:
            return await self.get_text_answer(answer_text=f'{username}\n{random.choice(rude_messages)}')
        return await self.get_text_answer(answer_text=random.choice(rude_messages))

    async def choose_variant(self) -> Optional[TextAnswerSchema]:
        choose_list = self.command_params.split(" или ")
        if len(choose_list) <= 1:
            choose_list = self.command_params.split(",")
        return await self.get_text_answer(answer_text=random.choice(choose_list).strip())

    async def get_quote(self) -> Optional[TextAnswerSchema]:
        quote = await ForismaticClient().get_quote_text()
        await self.count_stats(
            stats_enum=StatsEnum.QUOTER,
        )
        return await self.get_text_answer(answer_text=f"{quote.text}\n\n© {quote.author}")

    async def get_insult(self) -> Optional[TextAnswerSchema]:
        username = None
        if self.message.reply:
            username = f'@{self.message.reply.source.username}'
        evil_insult = await EvilInsultClient().get_evil_insult()
        await self.count_stats(
            stats_enum=StatsEnum.EVIL_INSULT,
        )
        insult = f"{evil_insult.insult}\n\n© {evil_insult.comment}"
        if username:
            return await self.get_text_answer(answer_text=f"{username}\n{insult}")
        return await self.get_text_answer(answer_text=insult)

    async def get_num(self) -> Optional[VoiceAnswerSchema]:
        condition = Property.slug == PropertiesEnum.DIGITS.name
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

    async def get_chance(self) -> Optional[TextAnswerSchema]:
        return await self.get_text_answer(answer_text=f"Есть вероятность "
                                                      f"{self.command_params} - "
                                                      f"{str(random.randint(0, 100))}%")

    async def get_joke(self) -> Optional[TextAnswerSchema]:
        JokeVendor = random.choice([BashOrgClient, ])
        joke_vendor = JokeVendor()
        text = await joke_vendor.get_text()

        if text is None:
            return None
        return await self.get_text_answer(answer_text=f"{text}\n\n© {joke_vendor.url}")

    async def get_great_advice(self) -> Optional[TextAnswerSchema]:
        advice = await GreatAdviceClient().get_advice()
        await self.count_stats(
            stats_enum=StatsEnum.ADVICE,
        )
        return await self.get_text_answer(answer_text=advice.text)

    async def help(self) -> Optional[TextAnswerSchema]:
        return await self.get_text_answer(answer_text="https://hlebbot.ru/help")
