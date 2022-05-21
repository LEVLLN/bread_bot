from sqlalchemy import Column, String, Boolean, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins
from bread_bot.telegramer.schemas.telegram_messages import MessageSchema


class Member(mixins.AbstractIsActiveBaseModel,
             mixins.BaseModel,
             mixins.CRUDMixin):
    __tablename__ = 'members'

    member_id = Column(BigInteger, nullable=True)
    username = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_bot = Column(Boolean, default=False)
    stats = relationship(
        'Stats',
        back_populates='member',
        cascade='all, delete-orphan')
    chats = relationship(
        'ChatToMember',
        back_populates='member')

    @classmethod
    async def handle_by_message(cls, message: MessageSchema, db: AsyncSession) -> "Member":
        member = message.source
        instance = await cls.async_first(
            db=db,
            where=cls.username == member.username
        )
        if instance is None:
            instance: cls = await cls.async_add_by_kwargs(
                db=db,
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name,
                is_bot=member.is_bot,
                member_id=member.id
            )
        else:
            is_updated = False
            if member.id != instance.member_id:
                instance.member_id = member.id
                is_updated = True
            for key in ('username', 'first_name', 'last_name'):
                if getattr(member, key, None) != getattr(instance, key, None):
                    setattr(instance, key, getattr(member, key))
                    is_updated = True
            if is_updated:
                instance: cls = await cls.async_add(
                    db=db,
                    instance=instance,
                )
        return instance
