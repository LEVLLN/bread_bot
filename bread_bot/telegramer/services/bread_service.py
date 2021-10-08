import logging
import random
import re
from collections import defaultdict
from typing import List, Union, Dict, Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.models import Stats, Member, LocalMeme, Chat
from bread_bot.telegramer.models.chats_to_members import ChatToMember
from bread_bot.telegramer.schemas.telegram_messages import MessageSchema, \
    MemberSchema
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import StatsEnum, LocalMemeTypesEnum

logger = logging.getLogger(__name__)


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
        self.command: Optional[str] = None
        self.params: Optional[str] = None
        self.trigger_word: Optional[str] = None
        self.reply_to_message: bool = True

    @staticmethod
    def composite_mask(collection, split=True) -> str:
        mask_part = '\\b{}\\b' if split else '{}'
        return '|'.join(
            map(
                lambda x: mask_part.format(x),
                collection,
            )
        )

    async def parse_incoming_message(self):
        meme_name = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )
        command_collection = list(structs.COMMANDS_MAPPER.keys())

        if meme_name is not None:
            command_collection += list(meme_name.data.keys())

        command_mask = self.composite_mask(command_collection)
        groups = re.findall(
            f'^({self.trigger_mask})\\s({command_mask})?',
            self.message.text,
            re.IGNORECASE
        )
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
        if not has_trigger_word:
            raise ValueError('Is not Command')

    async def count_stats(
            self,
            member_db: Member,
            stats_enum: StatsEnum) -> Stats:
        stats = await Stats.async_first(
            db=self.db,
            filter_expression=and_(
                Stats.member_id == member_db.id,
                Stats.slug == stats_enum.name,
                Stats.chat_id == self.chat_id
            )
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
            db=self.db,
            filter_expression=Member.username == member.username
        )
        if member_db is None:
            member_db: Member = await Member.async_add(
                db=self.db,
                instance=Member(
                    username=member.username,
                    first_name=member.first_name,
                    last_name=member.last_name,
                    is_bot=member.is_bot,
                )
            )
        else:
            is_updated = False
            if member.id != member_db.member_id:
                member_db.member_id = member.id
                is_updated = True
            for key in ('username', 'first_name', 'last_name'):
                if getattr(member, key, None) != getattr(member_db, key, None):
                    setattr(member_db, key, getattr(member, key))
                    is_updated = True
            if is_updated:
                member_db: Member = await Member.async_add(
                    db=self.db,
                    instance=member_db,
                )
        return member_db

    async def handle_chat(self) -> Chat:
        title = self.message.chat.title \
            if self.message.chat.title is not None \
            else self.message.source.username

        chat_db: Chat = await Chat.async_first(
            db=self.db,
            filter_expression=Chat.chat_id == self.chat_id,
        )
        if chat_db is None:
            chat_db: Chat = await Chat.async_add(
                db=self.db,
                instance=Chat(
                    name=title,
                    chat_id=self.chat_id
                )
            )
        elif chat_db.name != title:
            chat_db.name = title
            chat_db = await Chat.async_add(
                db=self.db,
                instance=chat_db,
            )
            logger.info(f'Чат {self.chat_id} обновил название на {title}')
        return chat_db

    async def handle_chats_to_members(self, member_id: int, chat_id: int):
        member: Member = await Member.async_first(
            db=self.db,
            filter_expression=Member.id == member_id,
            select_in_load=Member.chats
        )
        chat: Chat = await Chat.async_first(
            db=self.db,
            filter_expression=Chat.id == chat_id
        )
        if not member or not chat:
            return
        if chat.id in [chat.chat_id for chat in member.chats]:
            return

        member.chats.append(ChatToMember(chat_id=chat_id))
        await member.commit(db=self.db)
        return

    async def get_unknown_messages(self) -> list:
        unknown_message_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )
        unknown_messages = structs.DEFAULT_UNKNOWN_MESSAGE.copy()
        if unknown_message_db is not None:
            unknown_messages.extend(unknown_message_db.data)
        return unknown_messages

    async def handle_free_words(self) -> Optional[str]:
        free_words_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        free_words = structs.FREE_WORDS.copy()
        if free_words_db is not None:
            free_words.update(**free_words_db.data)
        message_text = self.message.text.lower().strip()
        if message_text not in free_words:
            return None
        value = free_words.get(message_text, 'упс!')
        if value == 'F':
            self.reply_to_message = False
        if isinstance(value, list):
            return random.choice(value)
        return value

    async def handle_substring_words(self) -> Optional[str]:
        substring_words_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
        )
        if substring_words_db is None:
            return None
        substring_words = substring_words_db.data
        if not substring_words:
            return None

        substring_words_mask = self.composite_mask(
            collection=substring_words.keys(),
            split=True,
        )
        regex = f'({substring_words_mask})'
        groups = re.findall(regex, self.message.text, re.IGNORECASE)
        if len(groups) > 0:
            substring_word = groups[0]
            value = substring_words.get(substring_word.lower().strip(), 'упс!')
            if isinstance(value, list):
                return random.choice(value)
            else:
                return value
        return None

    @staticmethod
    async def regular_phrases(
            meme_name: str,
            meme_name_data: Union[Dict, List]
    ) -> str:
        meme_prefix = random.choice(
            structs.DEFAULT_PREFIX + [meme_name.capitalize(), ])
        meme_sequence = meme_name_data.get(meme_name, [])
        meme_value = random.choice(meme_sequence)

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
        meme_name, value = self.params.strip().split('=', 1)
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
            return f'Ура! У группы появились свои ключевые слова: {meme_type}'

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

    async def show_stats(self) -> str:
        statistics = defaultdict(str)
        for stat in await Stats.async_filter(
                db=self.db,
                filter_expression=Stats.chat_id == self.chat_id,
                select_in_load=Stats.member,
                order_by=Stats.count.desc()
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

    async def propagate_members_memes(self) -> str:
        if self.chat_id < 0:
            return 'Нельзя из чата копировать в другой чат. ' \
                   'Только из личных сообщений с ботом!'

        destination_chat: Chat = await Chat.async_first(
            db=self.db,
            filter_expression=Chat.name == self.params.strip(),
        )

        if destination_chat is None:
            return 'Не найдено чата для отправки'

        if destination_chat.chat_id > 0:
            return 'Невозможно копировать другим людям свои данные'

        if destination_chat.chat_id == self.chat_id:
            return 'Нельзя распространять себе в личку'

        member: Member = await Member.async_first(
            db=self.db,
            filter_expression=Member.username == self.message.source.username,
            select_in_load=Member.chats
        )

        if not member:
            return 'Что-то пошло не так'

        if destination_chat.id not in [chat.chat_id for chat in member.chats]:
            return 'Нет прав на указанный чат'

        destination_local_memes = await LocalMeme.async_filter(
            db=self.db,
            filter_expression=and_(
                LocalMeme.chat_id == destination_chat.chat_id,
                LocalMeme.type != LocalMemeTypesEnum.UNKNOWN_MESSAGE.name
            )
        )
        source_local_memes = await LocalMeme.async_filter(
            db=self.db,
            filter_expression=and_(
                LocalMeme.chat_id == self.chat_id,
                LocalMeme.type != LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
            )
        )

        if not source_local_memes or not destination_local_memes:
            return 'Не найдено данных для копирования'

        data_to_add = defaultdict(lambda: defaultdict(list))
        local_memes_types = [d.type for d in destination_local_memes]
        update_list = []

        for source_meme in source_local_memes:
            for k, v in source_meme.data.items():
                data_to_add[source_meme.type][k] = v
            if source_meme.type not in local_memes_types:
                update_list.append(
                    LocalMeme(
                        type=source_meme.type,
                        data=source_meme.data,
                        chat_id=destination_chat.chat_id,
                    )
                )

        for local_meme in destination_local_memes:
            data = local_meme.data.copy()
            has_updated = False

            for k, v_list in data_to_add[local_meme.type].items():
                if k in data:
                    has_updated = True
                    data[k] += v_list
                else:
                    has_updated = True
                    data[k] = v_list

            if has_updated:
                local_meme.data = data
                update_list.append(local_meme)

        if not update_list:
            return 'Нечего обновлять'

        await LocalMeme.async_add_all(self.db, update_list)
        return 'Сделал'
