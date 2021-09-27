import random
from collections import defaultdict
from typing import Optional

from bread_bot.telegramer.models import Stats, LocalMeme
from bread_bot.telegramer.schemas.telegram_messages import MemberSchema
from bread_bot.telegramer.services.bread_service import BreadService
from bread_bot.telegramer.services.forismatic_client import ForismaticClient
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import StatsEnum, LocalMemeTypesEnum


class BreadServiceHandler(BreadService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def build_message(self) -> Optional[str]:
        member_db = await self.handle_member(member=self.message.source)
        await self.handle_chat()

        if self.is_edited:
            await self.count_stats(
                member_db=member_db,
                stats_enum=StatsEnum.EDITOR,
            )
            return random.choice(structs.FAGGOT_EDITOR_MESSAGES)

        free_word = await self.handle_free_words()
        if free_word is not None:
            return free_word

        substring_word = await self.handle_substring_words()
        if substring_word is not None:
            return substring_word

        try:
            await self.parse_incoming_message()
        except Exception:
            await self.count_stats(
                member_db=member_db,
                stats_enum=StatsEnum.FLUDER,
            )
            return None

        await self.count_stats(
            member_db=member_db,
            stats_enum=StatsEnum.TOTAL_CALL_SLUG,
        )

        unknown_messages = await self.get_unknown_messages()
        if self.command is None:
            return random.choice(unknown_messages)

        meme_names_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )
        if meme_names_db is not None:
            if self.command in meme_names_db.data.keys() \
                    or self.command in structs.OTHER_DIALOGS.keys():
                return await self.regular_phrases(
                    meme_name=self.command,
                    meme_name_data=meme_names_db.data
                )

        if self.command in structs.COMMANDS_MAPPER.keys():
            method = getattr(self, structs.COMMANDS_MAPPER[self.command])
            return await method()

        return random.choice(unknown_messages)

    async def who_is(self) -> str:
        params = self.params.replace('?', '')
        member = random.choice(await self.get_members())
        username = await self.get_username(member)

        if params.strip().lower().startswith('пидор'):
            member_db = await self.handle_member(member)
            await self.count_stats(
                member_db=member_db,
                stats_enum=StatsEnum.FAGGOTER,
            )

        return f'{random.choice(structs.DEFAULT_PREFIX)} ' \
               f'{params} - это {username}'

    async def who_have_is(self) -> str:
        params = self.params.replace('?', '')
        member = random.choice(await self.get_members())
        username = await self.get_username(member)
        return f'{random.choice(structs.DEFAULT_PREFIX)} {params} у {username}'

    async def gey_double(self) -> str:
        members = await self.get_members()
        random.shuffle(members)
        return f'Гей-парочку образовали: ' \
               f'{await self.get_username(members[0])} ' \
               f'и {await self.get_username(members[1])}'

    async def top(self) -> str:
        members = await self.get_members()
        result = ''
        i = 1
        random.shuffle(members)
        for user in members:
            if not user:
                continue
            result += f'{i}) {await self.get_username(user)}\n'
            i += 1
        return f'Топ {self.params}:\n{result}'

    @staticmethod
    async def set_null() -> str:
        return '*Тут скоро будут пацанские цитаты или картиночки с волками*'

    @staticmethod
    async def wednesday() -> str:
        return '*пикча жабы* Это среда мои чуваки'

    @staticmethod
    async def thursday() -> str:
        return 'время лизнуть'

    @staticmethod
    async def tuesday() -> str:
        return 'https://images.ru.prom.st/537418649_b9-bayan-romans.jpg'

    @staticmethod
    async def f_func() -> str:
        return 'F'

    @staticmethod
    async def get_num() -> str:
        return str(random.randint(0, 100000000))

    async def get_chance(self) -> str:
        chances = structs.DEFAULT_CHANCE + \
                  [str(random.randint(0, 100)) + '%', ]
        return f'Есть вероятность {self.params} - {random.choice(chances)}'

    @staticmethod
    async def help() -> str:
        try:
            with open('About.md', 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception:
            return '...нет нихуя'
        else:
            return text

    async def choose_variant(self) -> str:
        choose_list = self.params.split(' или ')
        if len(choose_list) <= 1:
            choose_list = self.params.split(',')
        return random.choice(choose_list).strip()

    async def show_stats(self) -> str:
        statistics = defaultdict(str)
        for stat in await Stats.async_filter(
            session=self.db,
            filter_expression=Stats.chat_id == self.chat_id,
            select_in_load=Stats.member,
        ):
            member = MemberSchema(
                first_name=stat.member.first_name,
                last_name=stat.member.last_name,
                username=stat.member.username,
                is_bot=stat.member.is_bot,
            )
            row = f'{await self.get_username(member)} - {stat.count}'
            if statistics[stat.slug] == '':
                statistics[stat.slug] = row + '\n'
            else:
                statistics[stat.slug] += row + '\n'
        result = ''
        for stat_slug, value in statistics.items():
            result += f'{StatsEnum[stat_slug].value}:\n{value}\n\n'
        return result if result != '' else 'Пока не набрал статистики'

    async def add_local_meme_name(self):
        return await self.add_local_meme(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name)

    async def add_local_substring(self):
        return await self.add_local_meme(
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name)

    async def add_local_free_word(self):
        return await self.add_local_meme(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)

    async def delete_local_meme_name(self):
        return await self.delete_local_meme(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name)

    async def delete_local_substring(self):
        return await self.delete_local_meme(
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name)

    async def delete_local_free_word(self):
        return await self.delete_local_meme(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)

    async def show_local_meme_names(self):
        return await self.show_local_memes(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name)

    async def show_local_substrings(self):
        return await self.show_local_memes(
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name)

    async def show_local_free_words(self):
        return await self.show_local_memes(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)

    async def add_unknown_answer(self) -> str:
        return await self.add_list_value(
            meme_type=LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )

    @staticmethod
    async def get_quote() -> str:
        quote = await ForismaticClient().get_quote_text()
        return f'{quote.text}\n\n© {quote.author}'
