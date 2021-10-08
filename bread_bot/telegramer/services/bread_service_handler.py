import random
from typing import Optional

from sqlalchemy import and_

from bread_bot.telegramer.models import LocalMeme, Chat, Property, Member
from bread_bot.telegramer.services.bread_service import BreadService
from bread_bot.telegramer.services.forismatic_client import ForismaticClient
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import StatsEnum, LocalMemeTypesEnum, \
    PropertiesEnum


class BreadServiceHandler(BreadService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_db: Optional[Member] = None
        self.chat_db: Optional[Chat] = None

    async def build_message(self) -> Optional[str]:
        self.member_db = await self.handle_member(member=self.message.source)
        self.chat_db = await self.handle_chat()
        await self.handle_chats_to_members(self.member_db.id, self.chat_db.id)

        has_voice_sent = await self.send_fart_voice()
        if has_voice_sent:
            return None

        if self.is_edited:
            if self.chat_db.is_edited_trigger:
                condition = Property.slug == PropertiesEnum.ANSWER_TO_EDIT.name
                editor_messages: Property = await Property.async_first(
                    session=self.db,
                    filter_expression=condition,
                )
                if editor_messages is None or not editor_messages.data:
                    return
                await self.count_stats(
                    member_db=self.member_db,
                    stats_enum=StatsEnum.EDITOR,
                    value=StatsEnum.EDITOR.value,
                )
                return random.choice(editor_messages.data)
            else:
                return None

        free_word = await self.handle_free_words()
        if free_word is not None:
            return free_word

        substring_word = await self.handle_substring_words()

        try:
            await self.parse_incoming_message()
        except Exception:
            if substring_word is not None:
                return substring_word
            await self.count_stats(
                member_db=self.member_db,
                stats_enum=StatsEnum.FLUDER,
                value=StatsEnum.FLUDER.value,
            )
            return None

        await self.count_stats(
            member_db=self.member_db,
            stats_enum=StatsEnum.TOTAL_CALL_SLUG,
            value=StatsEnum.TOTAL_CALL_SLUG.value,
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
            if self.command in meme_names_db.data.keys():
                return await self.regular_phrases(
                    meme_name=self.command,
                    meme_name_data=meme_names_db.data
                )

        if self.command in structs.COMMANDS_MAPPER.keys():
            method = getattr(self, structs.COMMANDS_MAPPER[self.command])
            return await method()

        if substring_word is not None:
            return substring_word
        return random.choice(unknown_messages)

    async def who_is(self) -> str:
        params = self.params.replace('?', '')
        if self.chat_id > 0:
            member = self.message.source
        else:
            member = random.choice(await self.get_members())
        username = await self.get_username(member)
        who_stats_key_words = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.WHO_TO_STATS_KEYS.name,
        )
        who_stats_key_words_list = who_stats_key_words.data \
            if who_stats_key_words else []
        for key_word in who_stats_key_words_list:
            if key_word.strip().lower() == params.strip().lower():
                member_db = await self.handle_member(member)
                await self.count_stats(
                    member_db=member_db,
                    stats_enum=key_word,
                    value=f'Сколько бот приравнивал к слову {key_word}',
                )

        return f'{random.choice(structs.DEFAULT_PREFIX)} ' \
               f'{params} - это {username}'

    async def who_have_is(self) -> str:
        params = self.params.replace('?', '')
        if self.chat_id > 0:
            member = self.message.source
        else:
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

    async def add_who_choose_key(self) -> str:
        return await self.add_list_value(
            meme_type=LocalMemeTypesEnum.WHO_TO_STATS_KEYS.name,
        )

    async def get_quote(self) -> str:
        quote = await ForismaticClient().get_quote_text()
        await self.count_stats(
            member_db=self.member_db,
            stats_enum=StatsEnum.QUOTER,
            value=StatsEnum.QUOTER.value,
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
                and self.message.voice.duration >= 1\
                and self.chat_db.is_voice_trigger:
            condition = Property.slug == PropertiesEnum.BAD_VOICES.name
            fart_list: Property = await Property.async_first(
                session=self.db,
                filter_expression=condition,
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
