import logging
import random
import re
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.models import Member, LocalMeme, Chat
from bread_bot.telegramer.schemas.telegram_messages import MessageSchema
from bread_bot.telegramer.services.chat_service import ChatServiceMixin
from bread_bot.telegramer.services.member_service import MemberServiceMixin
from bread_bot.telegramer.services.phrases_service import PhrasesServiceMixin, PhrasesServiceHandlerMixin
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.services.utils_service import UtilsServiceMixin
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum

logger = logging.getLogger(__name__)


class BreadServiceHandler(
    ChatServiceMixin,
    PhrasesServiceMixin,
    PhrasesServiceHandlerMixin,
    UtilsServiceMixin,
    MemberServiceMixin,
):
    COMPLETE_MESSAGE = "Сделал"

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
        self.member_db: Optional[Member] = None
        self.chat_db: Optional[Chat] = None
        self.answer_chance: int = 100

    async def init_handler(self):
        self.member_db = await self.handle_member(member=self.message.source)
        self.chat_db = await self.handle_chat()
        await self.handle_chats_to_members(self.member_db.id, self.chat_db.id)
        await self.parse_incoming_message()

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
                if random.random() > self.answer_chance / 100:
                    return None
                return result

        return None

    @staticmethod
    def composite_mask(collection, split=True) -> str:
        mask_part = "\\b{}\\b" if split else "{}"
        return '|'.join(
            map(
                lambda x: mask_part.format(re.escape(x)),
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
            f"^({self.trigger_mask})\\s({command_mask})?",
            self.message.text,
            re.IGNORECASE
        )

        if len(groups) > 0:
            phrase = " ".join(groups[0])
            self.trigger_word = groups[0][0]
            self.command = groups[0][1].lower()
            self.params = self.message.text.replace(phrase, "").lstrip()