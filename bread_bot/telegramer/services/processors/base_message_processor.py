import logging
import random
import re
from abc import ABC
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.models import Member, Chat, Stats, LocalMeme
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema, BaseAnswerSchema, VoiceAnswerSchema, \
    PhotoAnswerSchema, StickerAnswerSchema
from bread_bot.telegramer.schemas.telegram_messages import MessageSchema
from bread_bot.telegramer.services.message_service import MessageService
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.functions import composite_mask
from bread_bot.telegramer.utils.structs import StatsEnum, LocalMemeTypesEnum

logger = logging.getLogger(__name__)


class MessageProcessor(ABC):
    def __init__(self, message_service: MessageService):
        self.message_service: MessageService = message_service
        self.db: AsyncSession = self.message_service.db
        self.member: Member = self.message_service.member
        self.chat: Chat = self.message_service.chat
        self.message: MessageSchema = self.message_service.message
        self.trigger_word: Optional[str] = ""
        self.command: str = ""
        self.command_params: str = ""

    async def _process(self) -> Optional[BaseAnswerSchema]:
        """Контекст процессора"""
        pass

    async def process(self) -> Optional[BaseAnswerSchema]:
        """Основная функция процессора"""
        try:
            await self.count_stats(stats_enum=StatsEnum.FLUDER)
            if not await self.condition:
                return None
            return await self._process()
        except Exception as e:
            logger.error(str(e))
            return await self.get_text_answer(answer_text=random.choice(structs.ERROR_CHAT_MESSAGES))

    @property
    async def condition(self) -> bool:
        """Условие, при котором отработает Processor"""
        return True

    async def get_text_answer(self, answer_text: str, to_reply: bool = True) -> TextAnswerSchema:
        """Вернуть текстовый ответ"""
        return TextAnswerSchema(
            reply_to_message_id=self.message.message_id if to_reply else None,
            chat_id=self.chat.chat_id,
            text=answer_text,
        )

    async def get_voice_answer(self, voice: str, to_reply: bool = True) -> VoiceAnswerSchema:
        return VoiceAnswerSchema(
            reply_to_message_id=self.message.message_id if to_reply else None,
            chat_id=self.chat.chat_id,
            voice=voice,
        )

    async def get_photo_answer(self, photo: str, to_reply: bool = True) -> PhotoAnswerSchema:
        return PhotoAnswerSchema(
            reply_to_message_id=self.message.message_id if to_reply else None,
            chat_id=self.chat.chat_id,
            photo=photo,
        )

    async def get_sticker_answer(self, sticker: str, to_reply: bool = True) -> StickerAnswerSchema:
        return StickerAnswerSchema(
            reply_to_message_id=self.message.message_id if to_reply else None,
            chat_id=self.chat.chat_id,
            sticker=sticker,
        )

    async def count_stats(
            self,
            stats_enum: StatsEnum,
    ) -> Stats:
        """Посчитать статистику"""
        member_id = self.member.id
        stats = await Stats.async_first(
            db=self.db,
            where=and_(
                Stats.member_id == member_id,
                Stats.slug == stats_enum.name,
                Stats.chat_id == self.chat.chat_id
            )
        )
        if stats is None:
            stats = await Stats.async_add_by_kwargs(
                db=self.db,
                member_id=member_id,
                slug=stats_enum.name,
                count=1,
                chat_id=self.chat.chat_id,
            )
        else:
            stats.count = stats.count + 1
        return await Stats.async_add(self.db, stats)

    async def parse_command(self, command_collection: list):
        """Парсинг сообщения на триггер, команду и параметры"""
        if not self.message.text:
            return

        groups = re.findall(
            f"^({await composite_mask(structs.TRIGGER_WORDS)})\\s({await composite_mask(command_collection)})?",
            self.message.text,
            re.IGNORECASE
        )

        if len(groups) > 0:
            phrase = " ".join(groups[0])
            self.trigger_word = groups[0][0]
            self.command = groups[0][1].lower()
            self.command_params = self.message.text.replace(phrase, "").lstrip()

    async def parse_sub_command(self, sub_command_collection: dict):
        """Парсинг команды на подкоманды и параметры"""
        sub_command = None
        key = None
        value = None

        groups = re.findall(
            f"^({await composite_mask(sub_command_collection.keys())})\\s(.*)",
            self.command_params,
            re.IGNORECASE
        )

        if len(groups) > 0:
            sub_command = sub_command_collection[groups[0][0]]
            spited_params = groups[0][1].strip().lower().split("=")
            key = spited_params[0]
            value = spited_params[1] if len(spited_params) > 1 else None
        return sub_command, key, value

    async def get_list_messages(
            self,
            meme_type: str = LocalMemeTypesEnum.UNKNOWN_MESSAGE.name) -> list:
        unknown_message_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=meme_type,
        )
        if meme_type == LocalMemeTypesEnum.UNKNOWN_MESSAGE.name:
            unknown_messages = structs.DEFAULT_UNKNOWN_MESSAGE.copy()
        else:
            unknown_messages = list()
        if unknown_message_db is not None:
            unknown_messages.extend(unknown_message_db.data)
        return unknown_messages
