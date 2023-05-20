import logging

from sqlalchemy import BigInteger, Column, SmallInteger, String
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins

logger = logging.getLogger(__name__)


class Chat(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "chats"

    chat_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    morph_answer_chance = Column(SmallInteger, default=15, nullable=False)

    members = relationship("ChatToMember", back_populates="chat")
    answer_packs = relationship("AnswerPacksToChats", back_populates="chats")
    dictionary_entities = relationship("DictionaryEntity", back_populates="chats")
