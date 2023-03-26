import datetime
import logging

from asyncpg import UniqueViolationError
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.models import Chat, ChatToMember, Member
from bread_bot.common.schemas.telegram_messages import MessageSchema

logger = logging.getLogger(__name__)


class MemberService:
    """
    Сервис обработки пользователей и чатов
    """

    def __init__(self, db: AsyncSession, message: MessageSchema):
        self.db: AsyncSession = db
        self.message: MessageSchema = message
        self.member: Member | None = None
        self.chat: Chat | None = None

    async def handle_member(self) -> Member:
        member = self.message.source
        if member.username == "":
            member.username = member.id
        instance = await Member.async_first(
            db=self.db,
            where=or_(
                Member.member_id == member.id,
                Member.username == member.username,
            ),
        )
        if instance is None:
            instance: Member = await Member.async_add_by_kwargs(
                db=self.db,
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name,
                is_bot=member.is_bot,
                member_id=member.id,
            )
        else:
            is_updated = False
            for key in ("username", "first_name", "last_name"):
                if getattr(member, key, None) != getattr(instance, key, None):
                    setattr(instance, key, getattr(member, key))
                    is_updated = True
            if is_updated:
                try:
                    instance: Member = await Member.async_add(
                        db=self.db,
                        instance=instance,
                    )
                except UniqueViolationError as e:
                    logger.info("Не получилось сохранить username, first_name, last_name %s", str(e))
        return instance

    async def handle_chat(self) -> Chat:
        title = self.message.chat.title if self.message.chat.title is not None else self.message.source.username

        instance: Chat = await Chat.async_first(
            db=self.db,
            where=Chat.chat_id == self.message.chat.id,
        )
        if instance is None:
            instance: Chat = await Chat.async_add_by_kwargs(db=self.db, name=title, chat_id=self.message.chat.id)
        elif instance.name != title:
            instance.name = title
            instance = await Chat.async_add(
                db=self.db,
                instance=instance,
            )
        return instance

    async def bind_chat_to_member(self) -> bool:
        chat_to_member = await ChatToMember.async_first(
            db=self.db,
            where=and_(
                ChatToMember.member_id == self.member.id,
                ChatToMember.chat_id == self.chat.id,
            ),
        )
        if not chat_to_member:
            await ChatToMember.async_add(
                db=self.db,
                instance=ChatToMember(
                    chat_id=self.chat.id, member_id=self.member.id, updated_at=datetime.datetime.now()
                ),
            )
        else:
            chat_to_member.updated_at = datetime.datetime.now()
            await ChatToMember.async_add(self.db, chat_to_member)
        logger.info("Member %s bind with chat %s", self.member.id, self.chat.id)
        return True

    async def process(self):
        self.member = await self.handle_member()
        self.chat = await self.handle_chat()
        if self.member and self.chat:
            await self.bind_chat_to_member()
