import logging

from sqlalchemy import Column, String, BigInteger, SmallInteger, Boolean
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins

logger = logging.getLogger(__name__)


class Chat(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "chats"

    chat_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    morph_answer_chance = Column(SmallInteger, default=15, nullable=False)
    is_openai_enabled = Column(Boolean, default=False, nullable=False)
    members = relationship("ChatToMember", back_populates="chat")
    answer_packs = relationship("AnswerPacksToChats", back_populates="chats")
    dictionary_entities = relationship("DictionaryEntity", back_populates="chats")
