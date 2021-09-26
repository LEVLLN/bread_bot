import random
import re
from typing import List, Union, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.models import Stats, Member, LocalMeme
from bread_bot.telegramer.schemas.telegram_messages import MessageSchema, \
    MemberSchema
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import StatsEnum, LocalMemeTypesEnum


class BreadService:
    def __init__(
            self,
            client: TelegramClient,
            message: MessageSchema,
            db: AsyncSession,
            is_edited: bool = False,
    ):
        self.client = client
        self.message = message
        self.chat_id = self.message.chat.id
        self.is_edited = is_edited
        self.db = db
        self.trigger_mask = self.composite_mask(structs.TRIGGER_WORDS)
        self.command = None
        self.params = None
        self.trigger_word = None
        self.reply_to_message = True

    @staticmethod
    def composite_mask(collection) -> str:
        return '|'.join(
            map(
                lambda x: f'\\b{x}\\b',
                collection,
            )
        )

    async def parse_incoming_message(self):
        meme_name = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )
        command_collection = structs.COMMANDS_COLLECTION

        if meme_name is not None:
            command_collection += list(meme_name.data.keys())

        command_mask = self.composite_mask(command_collection)
        regex = f'^({self.trigger_mask})\\s({command_mask})?'
        groups = re.findall(regex, self.message.text, re.IGNORECASE)
        has_trigger_word = False

        for trigger_word in structs.TRIGGER_WORDS:
            if self.message.text.lower().startswith(trigger_word):
                has_trigger_word = True
                break
        if len(groups) > 0:
            phrase = ' '.join(groups[0])
            self.trigger_word = groups[0][0]
            self.command = groups[0][1].lower()
            self.params = self.message.text.replace(phrase, '').lstrip()
            return
        if has_trigger_word:
            return
        raise ValueError('Is not Command')

    async def count_stats(
            self,
            member_db: Member,
            stats_enum: StatsEnum) -> Stats:
        stats = await Stats.async_first(
            session=self.db,
            filter_expression=(Stats.member_id == member_db.id) &
                              (Stats.slug == stats_enum.name) &
                              (Stats.chat_id == self.chat_id),
        )
        if stats is None:
            stats = await Stats.async_add(
                db=self.db,
                instance=Stats(
                    member_id=member_db.id,
                    slug=stats_enum.name,
                    count=1,
                    chat_id=self.chat_id,
                ),
            )
        else:
            stats.count = stats.count + 1
        return await Stats.async_add(self.db, stats)

    async def handle_member(self, member: MemberSchema) -> Member:
        member_db = await Member.async_first(
            session=self.db,
            filter_expression=Member.username == member.username
        )
        if member_db is None:
            member_db = await Member.async_add(
                db=self.db,
                instance=Member(
                    username=member.username,
                    first_name=member.first_name,
                    last_name=member.last_name,
                    is_bot=member.is_bot,
                )
            )
        return member_db

    async def get_free_words(self) -> dict:
        free_words_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        free_words = structs.FREE_WORDS
        if free_words_db is not None:
            free_words.update(**free_words_db.data)
        return free_words

    async def get_unknown_messages(self) -> list:
        unknown_message_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )
        unknown_messages = structs.DEFAULT_UNKNOWN_MESSAGE
        if unknown_message_db is not None:
            unknown_messages.extend(unknown_message_db.data)
        return unknown_messages

    async def handle_free_words(self, free_words: dict) -> str:
        value = free_words.get(self.message.text.lower().strip(), 'пнх')
        if value == 'f':
            self.reply_to_message = False
        if isinstance(value, list):
            return random.choice(value)
        return value

    @staticmethod
    async def regular_phrases(
            meme_name: str,
            meme_name_data: Union[Dict, List]
    ) -> str:
        meme_prefix = random.choice(
            structs.DEFAULT_PREFIX + [meme_name.capitalize(), ])
        meme_sequence = meme_name_data.get(meme_name, []) + \
            structs.OTHER_DIALOGS.get(meme_name, [])
        meme_value = random.choice(meme_sequence)

        if meme_name in structs.OTHER_DIALOGS.keys() or meme_prefix == '':
            return meme_value
        return meme_prefix + ' ' + meme_value

    @staticmethod
    async def get_username(member: MemberSchema) -> str:
        user_name = ''
        if member.first_name != '' or member.last_name != '':
            user_name = f'{member.first_name.strip()} ' \
                        f'{member.last_name.strip()}'

        if user_name.strip().replace('ㅤ', '') == '':
            user_name = f'@{member.username.capitalize()}'
        return user_name.strip()

    async def get_members(self) -> List[MemberSchema]:
        response = await self.client.get_chat(self.chat_id)
        chats = response.result
        return [chat.user for chat in chats if not chat.user.is_bot]

    async def add_local_meme(self, meme_type: str) -> str:
        meme_name, value = self.params.strip().split('=')
        meme_name = meme_name.lower().strip()
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            await LocalMeme.async_add(
                self.db,
                LocalMeme(
                    chat_id=self.chat_id,
                    type=meme_type,
                    data={meme_name: [value]}
                )
            )
            return 'Ура! У группы появились свои ключевые слова'

        data = local_meme.data.copy()

        if meme_name in data.keys():
            meme_list = data[meme_name].copy()
            meme_list.append(value)
            data[meme_name] = meme_list
        else:
            data[meme_name] = [value]

        local_meme.data = data
        await LocalMeme.async_add(self.db, local_meme)

        return 'Сделал'

    async def delete_local_meme(self, meme_type: str) -> str:
        value = self.params.strip().lower()
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            return 'У чата нет своих ключевых слов'

        data = local_meme.data.copy()
        if value in data.keys():
            del data[value]
        else:
            return 'Ключевого слова и не было'

        local_meme.data = data
        await LocalMeme.async_add(self.db, local_meme)
        return 'Сделал'

    async def show_local_memes(self, meme_type: str) -> str:
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            return 'У группы еще нет локальных ключевых слов'
        if not local_meme.data:
            return 'У группы еще нет локальных ключевых слов'
        return '\n'.join(local_meme.data.keys())

    async def add_list_value(self, meme_type: str) -> str:
        value = self.params.strip()
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            await LocalMeme.async_add(
                self.db,
                LocalMeme(
                    chat_id=self.chat_id,
                    type=meme_type,
                    data=[value]
                )
            )
            return 'Ура! У группы появились свои оригинальные ответы'

        data = local_meme.data.copy()
        data.append(value)
        local_meme.data = data
        await LocalMeme.async_add(self.db, local_meme)
        return 'Сделал'
