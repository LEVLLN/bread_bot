import logging

from sqlalchemy import Column, String, BigInteger, Boolean, SmallInteger
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins

logger = logging.getLogger(__name__)


class Chat(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "chats"

    chat_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    is_edited_trigger = Column(Boolean, default=False, nullable=False)
    is_voice_trigger = Column(Boolean, default=False, nullable=False)
    answer_chance = Column(SmallInteger, default=100, nullable=False)

    members = relationship("ChatToMember", back_populates="chat")
    answer_packs = relationship("AnswerPacksToChats", back_populates="chats")
