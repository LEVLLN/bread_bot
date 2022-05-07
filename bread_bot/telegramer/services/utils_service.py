import random

from bread_bot.telegramer.clients.evil_insult_client import EvilInsultClient
from bread_bot.telegramer.clients.forismatic_client import ForismaticClient
from bread_bot.telegramer.utils.structs import StatsEnum


class UtilsServiceMixin:
    @staticmethod
    async def help() -> str:
        return "https://telegra.ph/HlebushekBot-10-04-3"

    async def choose_variant(self) -> str:
        choose_list = self.params.split(" или ")
        if len(choose_list) <= 1:
            choose_list = self.params.split(",")
        return random.choice(choose_list).strip()

    async def get_quote(self) -> str:
        quote = await ForismaticClient().get_quote_text()
        await self.count_stats(
            member_db=self.member_db,
            stats_enum=StatsEnum.QUOTER,
        )
        return f'{quote.text}\n\n© {quote.author}'

    async def get_insult(self) -> str:
        username = None
        if self.message.reply:
            username = f'@{self.message.reply.source.username}'
        evil_insult = await EvilInsultClient().get_evil_insult()
        await self.count_stats(
            member_db=self.member_db,
            stats_enum=StatsEnum.EVIL_INSULT,
        )
        insult = f"{evil_insult.insult}\n\n© {evil_insult.comment}"
        if username:
            return f"{username}\n{insult}"
        return insult

    @staticmethod
    async def get_num() -> str:
        return str(random.randint(0, 100000000))

    async def get_chance(self) -> str:
        return f"Есть вероятность {self.params} - " \
               f"{str(random.randint(0, 100))}%"
