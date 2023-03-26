import logging

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins

logger = logging.getLogger(__name__)


class Chat(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "chats"

    chat_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String(255), nullable=True)

    members = relationship("ChatToMember", back_populates="chat")
    answer_packs = relationship("AnswerPacksToChats", back_populates="chats")
