import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.models import Member, Chat, ChatToMember
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
        instance = await Member.async_first(db=self.db, where=Member.username == member.username)
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
            if member.id != instance.member_id:
                instance.member_id = member.id
                is_updated = True
            for key in ("username", "first_name", "last_name"):
                if getattr(member, key, None) != getattr(instance, key, None):
                    setattr(instance, key, getattr(member, key))
                    is_updated = True
            if is_updated:
                instance: Member = await Member.async_add(
                    db=self.db,
                    instance=instance,
                )
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

    async def bind_chat_to_member(self, member_id: int, chat_id: int) -> bool:
        if member_id is None:
            return False
        member: Member = await Member.async_first(db=self.db, where=Member.id == member_id, select_in_load=Member.chats)
        chat: Chat = await Chat.async_first(db=self.db, where=Chat.id == chat_id)
        if not member or not chat:
            return False
        if chat.id in [chat.chat_id for chat in member.chats]:
            member.chats[0].updated_at = datetime.datetime.now()
            await ChatToMember.async_add(db=self.db, instance=member.chats[0])
            await member.commit(db=self.db)
            return False
        member.chats.append(ChatToMember(chat_id=chat_id, member_id=member_id))
        await member.commit(db=self.db)
        logger.info("Member %s bind with chat %s", member_id, chat_id)
        return True

    async def process(self):
        self.member = await self.handle_member()
        self.chat = await self.handle_chat()
        await self.bind_chat_to_member(self.member.id, self.chat.id)
