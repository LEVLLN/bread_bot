import random
from typing import Optional

from bread_bot.telegramer.models import Chat, Property
from bread_bot.telegramer.services.bread_service import BreadService
from bread_bot.telegramer.services.forismatic_client import ForismaticClient
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import StatsEnum, LocalMemeTypesEnum, \
    PropertiesEnum


class BreadServiceHandler(BreadService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def build_message(self) -> Optional[str]:
        await self.init_handler()

        if self.trigger_word:
            await self.count_stats(
                member_db=self.member_db,
                stats_enum=StatsEnum.TOTAL_CALL_SLUG,
            )

        for handler in [
            self.send_fart_voice,
            self.handle_edited_words,
            self.handle_command_words,
            self.handle_free_words,
            self.handle_bind_words,
            self.handle_substring_words,
            self.handle_unknown_words
        ]:
            result = await handler()

            if result:
                return result

        return None

    async def who_is(self) -> str:
        params = self.params.replace('?', '')
        username = await self.get_one_of_group()
        return f'{random.choice(structs.DEFAULT_PREFIX)} ' \
               f'{params} - это {username}'

    async def who_have_is(self) -> str:
        params = self.params.replace('?', '')
        username = await self.get_one_of_group()
        return f'{random.choice(structs.DEFAULT_PREFIX)} {params} у {username}'

    async def gey_double(self) -> str:
        members = await self.get_members()
        random.shuffle(members)
        return f'Гей-парочку образовали: ' \
               f'{await self.get_username(members[0])} ' \
               f'и {await self.get_username(members[1])}'

    async def top(self) -> str:
        if self.chat_id > 0:
            members = [self.message.source]
        else:
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
    async def get_num() -> str:
        return str(random.randint(0, 100000000))

    async def get_chance(self) -> str:
        chances = structs.DEFAULT_CHANCE + \
                  [str(random.randint(0, 100)) + '%', ]
        return f'Есть вероятность {self.params} - {random.choice(chances)}'

    @staticmethod
    async def help() -> str:
        return 'https://telegra.ph/HlebushekBot-10-04-3'

    async def choose_variant(self) -> str:
        choose_list = self.params.split(' или ')
        if len(choose_list) <= 1:
            choose_list = self.params.split(',')
        return random.choice(choose_list).strip()

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

    async def add_remember_phrase(self) -> str:
        if not self.message.reply or not self.params:
            return 'Выбери сообщение, которое запомнить'
        self.params = f'{self.message.reply.text}={self.params}'
        return await self.add_local_meme(
            meme_type=LocalMemeTypesEnum.REMEMBER_PHRASE.name,
        )

    async def get_quote(self) -> str:
        quote = await ForismaticClient().get_quote_text()
        await self.count_stats(
            member_db=self.member_db,
            stats_enum=StatsEnum.QUOTER,
        )
        return f'{quote.text}\n\n© {quote.author}'

    async def set_edited_trigger(self):
        self.chat_db.is_edited_trigger = not self.chat_db.is_edited_trigger
        self.chat_db = await Chat.async_add(
            db=self.db,
            instance=self.chat_db,
        )
        message = 'Включено' if self.chat_db.is_edited_trigger else 'Выключено'
        return f'{message} реагирование на редактирование сообщений'

    async def set_voice_trigger(self):
        self.chat_db.is_voice_trigger = not self.chat_db.is_voice_trigger
        self.chat_db = await Chat.async_add(
            db=self.db,
            instance=self.chat_db,
        )
        message = 'Включено' if self.chat_db.is_voice_trigger else 'Выключено'
        return f'{message} реагирование на голосовые сообщения'

    async def send_fart_voice(self):
        if self.message.voice is not None \
                and self.message.voice.duration \
                and self.message.voice.duration >= 1 \
                and self.chat_db.is_voice_trigger:
            condition = Property.slug == PropertiesEnum.BAD_VOICES.name
            fart_list: Property = await Property.async_first(
                db=self.db,
                where=condition,
            )
            if not fart_list or not fart_list.data:
                return False
            await self.client.send_voice(
                chat_id=self.chat_id,
                voice_file_id=random.choice(fart_list.data),
                reply_to=self.message.message_id,
            )
            return True
        return False
