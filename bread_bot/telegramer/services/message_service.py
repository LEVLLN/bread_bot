from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.telegramer.models import Chat, Member, ChatToMember
from bread_bot.telegramer.schemas.telegram_messages import StandardBodySchema, MessageSchema


class MessageService(object):
    """Сервис сообщений"""
    def __init__(
            self,
            request_body: StandardBodySchema = None,
            db: AsyncSession = None
    ):
        self.request_body: StandardBodySchema = request_body
        self.db = db
        self.chat: Optional[Chat] = None
        self.member: Optional[Member] = None
        self.message: Optional[MessageSchema] = None

    async def init(self):
        self.message = await self.get_message()
        self.chat = await Chat.handle_by_message(db=self.db, message=self.message)
        self.member = await Member.handle_by_message(db=self.db, message=self.message)
        await self.bind_chat_to_member()

    async def bind_chat_to_member(self) -> bool:
        return await ChatToMember.bind_by_ids(
            member_id=self.member.id,
            chat_id=self.chat.id,
            db=self.db,
        )

    @property
    async def has_message(self) -> bool:
        """Проверка тела запроса на наличие сообщения"""
        return hasattr(self.request_body, 'message') and self.request_body.message is not None

    @property
    async def has_edited_message(self) -> bool:
        """Проверка тела запроса на наличие отредактированного сообщения"""
        return hasattr(self.request_body, 'edited_message') and self.request_body.edited_message is not None

    async def get_message(self) -> MessageSchema:
        """Получение редактированного или обычного сообщения в качестве основного"""
        if await self.has_edited_message:
            return self.request_body.edited_message
        else:
            return self.request_body.message
