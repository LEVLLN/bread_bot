import logging
import random
from collections import defaultdict

from sqlalchemy import and_

from bread_bot.telegramer.models import Chat, Property, Member, ChatToMember, Stats, LocalMeme
from bread_bot.telegramer.schemas.telegram_messages import MemberSchema
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import StatsEnum, LocalMemeTypesEnum

logger = logging.getLogger(__name__)


class ChatServiceMixin:
    async def count_stats(
            self,
            member_db: Member,
            stats_enum: StatsEnum) -> Stats:
        stats = await Stats.async_first(
            db=self.db,
            where=and_(
                Stats.member_id == member_db.id,
                Stats.slug == stats_enum.name,
                Stats.chat_id == self.chat_id
            )
        )
        if stats is None:
            stats = await Stats.async_add_by_kwargs(
                db=self.db,
                member_id=member_db.id,
                slug=stats_enum.name,
                count=1,
                chat_id=self.chat_id,
            )
        else:
            stats.count = stats.count + 1
        return await Stats.async_add(self.db, stats)

    async def handle_chat(self) -> Chat:
        title = self.message.chat.title \
            if self.message.chat.title is not None \
            else self.message.source.username

        chat_db: Chat = await Chat.async_first(
            db=self.db,
            where=Chat.chat_id == self.chat_id,
        )
        if chat_db is None:
            chat_db: Chat = await Chat.async_add_by_kwargs(
                db=self.db,
                name=title,
                chat_id=self.chat_id
            )
        elif chat_db.name != title:
            chat_db.name = title
            chat_db = await Chat.async_add(
                db=self.db,
                instance=chat_db,
            )
            logger.info(f'Чат {self.chat_id} обновил название на {title}')
        if chat_db:
            self.answer_chance = chat_db.answer_chance
        return chat_db

    async def handle_chats_to_members(self, member_id: int, chat_id: int):
        member: Member = await Member.async_first(
            db=self.db,
            where=Member.id == member_id,
            select_in_load=Member.chats
        )
        chat: Chat = await Chat.async_first(
            db=self.db,
            where=Chat.id == chat_id
        )
        if not member \
                or not chat \
                or chat.id in [chat.chat_id for chat in member.chats]:
            return

        member.chats.append(ChatToMember(chat_id=chat_id))
        await member.commit(db=self.db)
        return

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
            condition = Property.slug == structs.PropertiesEnum.BAD_VOICES.name
            fart_list: Property = await Property.async_first(
                db=self.db,
                where=condition,
            )
            if not fart_list or not fart_list.data:
                return None
            await self.client.send_voice(
                chat_id=self.chat_id,
                voice_file_id=random.choice(fart_list.data),
                reply_to=self.message.message_id,
            )
        return None

    async def set_answer_chance(self):
        error_message = "Некорректное значение. Необходимо ввести число от 0 до 100"
        try:
            value = int(self.params.strip())
        except ValueError:
            return error_message

        if value < 0 or value > 100:
            return error_message

        self.chat_db.answer_chance = value
        self.chat_db = await Chat.async_add(
            db=self.db,
            instance=self.chat_db,
        )
        return self.COMPLETE_MESSAGE

    async def show_stats(self) -> str:
        statistics = defaultdict(str)
        for stat in await Stats.async_filter(
                db=self.db,
                where=Stats.chat_id == self.chat_id,
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
            where=Chat.name == self.params.strip(),
        )

        if destination_chat is None:
            return 'Не найдено чата для отправки'

        if destination_chat.chat_id > 0 \
                or destination_chat.chat_id == self.chat_id:
            return 'Невозможно копировать другим людям свои данные'

        member: Member = await Member.async_first(
            db=self.db,
            where=Member.username == self.message.source.username,
            select_in_load=Member.chats
        )

        if not member:
            return 'Что-то пошло не так'

        if destination_chat.id not in [chat.chat_id for chat in member.chats]:
            return 'Нет прав на указанный чат'

        destination_local_memes = await LocalMeme.async_filter(
            db=self.db,
            where=and_(
                LocalMeme.chat_id == destination_chat.chat_id,
                LocalMeme.type != LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
                LocalMeme.type != LocalMemeTypesEnum.RUDE_WORDS.name,
                LocalMeme.type != LocalMemeTypesEnum.REMEMBER_PHRASE.name,
            )
        )
        source_local_memes = await LocalMeme.async_filter(
            db=self.db,
            where=and_(
                LocalMeme.chat_id == self.chat_id,
                LocalMeme.type != LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
                LocalMeme.type != LocalMemeTypesEnum.RUDE_WORDS.name,
                LocalMeme.type != LocalMemeTypesEnum.REMEMBER_PHRASE.name,
            )
        )

        if not source_local_memes and not destination_local_memes:
            return 'Не найдено данных для копирования'

        data_to_add = defaultdict(lambda: defaultdict(set))
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

            for k, v_set in data_to_add[local_meme.type].items():
                if k in data:
                    has_updated = True
                    result = set(data[k]).union(v_set)
                    data[k] = list(result)
                else:
                    has_updated = True
                    data[k] = list(v_set)

            if has_updated:
                local_meme.data = data
                update_list.append(local_meme)

        if not update_list:
            return 'Нечего обновлять'

        await LocalMeme.async_add_all(self.db, update_list)
        return self.COMPLETE_MESSAGE