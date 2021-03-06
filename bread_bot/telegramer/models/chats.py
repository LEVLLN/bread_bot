import logging

from sqlalchemy import Column, String, BigInteger, Boolean, SmallInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins
from bread_bot.telegramer.schemas.telegram_messages import MessageSchema

logger = logging.getLogger(__name__)


class Chat(mixins.AbstractIsActiveBaseModel,
           mixins.BaseModel,
           mixins.CRUDMixin):
    __tablename__ = 'chats'

    chat_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    is_edited_trigger = Column(Boolean, default=False, nullable=False)
    is_voice_trigger = Column(Boolean, default=False, nullable=False)
    answer_chance = Column(SmallInteger, default=100, nullable=False)

    stats = relationship(
        'Stats',
        back_populates='chat',
        cascade='all, delete-orphan')
    local_memes = relationship(
        'LocalMeme',
        back_populates='chat',
        cascade='all, delete-orphan')
    members = relationship(
        'ChatToMember',
        back_populates='chat')

    @classmethod
    async def handle_by_message(cls, message: MessageSchema, db: AsyncSession) -> "Chat":
        title = message.chat.title \
            if message.chat.title is not None \
            else message.source.username

        instance: cls = await cls.async_first(
            db=db,
            where=cls.chat_id == message.chat.id,
        )
        if instance is None:
            instance: cls = await cls.async_add_by_kwargs(
                db=db,
                name=title,
                chat_id=message.chat.id
            )
        elif instance.name != title:
            instance.name = title
            instance = await cls.async_add(
                db=db,
                instance=instance,
            )
            logger.info(f'Чат {message.chat.id} обновил название на {title}')
        return instance
