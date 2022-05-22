import logging
import random
from typing import Optional

from bs4 import BeautifulSoup

from bread_bot.telegramer.clients.bashorg_client import BashOrgClient
from bread_bot.telegramer.clients.evil_insult_client import EvilInsultClient
from bread_bot.telegramer.clients.forismatic_client import ForismaticClient
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.services.processors.base_command_processor import CommandMessageProcessor
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum

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

    async def get_num(self) -> Optional[TextAnswerSchema]:
        return await self.get_text_answer(answer_text=str(random.randint(0, 100000000)))

    async def get_chance(self) -> Optional[TextAnswerSchema]:
        return await self.get_text_answer(answer_text=f"Есть вероятность "
                                                      f"{self.command_params} - "
                                                      f"{str(random.randint(0, 100))}%")

    async def get_joke(self) -> Optional[TextAnswerSchema]:
        try:
            html = await BashOrgClient().get_quote()
        except Exception as e:
            logger.error(str(e))
            return None

        try:
            text = BeautifulSoup(html, "html.parser") \
                .find(name="div", recursive=True, id="quotes") \
                .div \
                .find("div", **{"class": None}) \
                .get_text(separator="\n")
        except Exception as e:
            logger.error(str(e))
            return None
        else:
            return await self.get_text_answer(answer_text=text)

    async def help(self) -> Optional[TextAnswerSchema]:
        return await self.get_text_answer(answer_text="https://hlebbot.ru/help")
