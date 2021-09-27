from typing import Union

from sqlalchemy import Column, String, BigInteger, JSON, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins


class LocalMeme(mixins.AbstractIsActiveBaseModel,
                mixins.BaseModel,
                mixins.CRUDMixin):
    __tablename__ = 'local_memes'

    chat_id = Column(
        BigInteger,
        ForeignKey('chats.chat_id', ondelete='CASCADE'),
        nullable=False)
    type = Column(String(255), nullable=False)
    data = Column(JSON, default=JSON.NULL, nullable=True)
    chat = relationship('Chat',
                        back_populates='local_memes',
                        cascade='all, delete-orphan')

    @classmethod
    async def get_local_meme(
            cls,
            db: AsyncSession,
            chat_id: Union[int, str],
            meme_type: str):
        return await cls.async_first(
            session=db,
            filter_expression=(cls.chat_id == chat_id) &
                              (cls.type == meme_type)
        )
