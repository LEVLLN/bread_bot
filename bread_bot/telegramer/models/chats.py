from sqlalchemy import Column, String, BigInteger, Boolean
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins


class Chat(mixins.AbstractIsActiveBaseModel,
           mixins.BaseModel,
           mixins.CRUDMixin):
    __tablename__ = 'chats'

    chat_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    is_edited_trigger = Column(Boolean, default=False, nullable=False)

    stats = relationship(
        'Stats',
        back_populates='chat',
        cascade='all, delete-orphan')
    local_memes = relationship(
        'LocalMeme',
        back_populates='chat',
        cascade='all, delete-orphan')
