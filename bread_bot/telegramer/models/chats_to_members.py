import logging

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins
from bread_bot.telegramer.models import Member, Chat

logger = logging.getLogger(__name__)


class ChatToMember(mixins.AbstractIsActiveBaseModel,
                   mixins.BaseModel,
                   mixins.CRUDMixin):
    __tablename__ = 'chats_to_members'

    member_id = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'))
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    member = relationship("Member", back_populates="chats")
    chat = relationship("Chat", back_populates="members")

    @classmethod
    async def bind_by_ids(cls, member_id: int, chat_id: int, db: AsyncSession) -> bool:
        member: Member = await Member.async_first(
            db=db,
            where=Member.id == member_id,
            select_in_load=Member.chats
        )
        chat: Chat = await Chat.async_first(
            db=db,
            where=Chat.id == chat_id
        )
        if not member \
                or not chat \
                or chat.id in [chat.chat_id for chat in member.chats]:
            return False

        member.chats.append(cls(chat_id=chat_id, member_id=member_id))
        await member.commit(db=db)
        logger.info("Member %s bind with chat %s", member_id, chat_id)
        return True
