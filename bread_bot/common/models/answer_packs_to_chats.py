import logging

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins

logger = logging.getLogger(__name__)


class AnswerPacksToChats(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "answer_packs_to_chats"

    pack_id = Column(Integer, ForeignKey("answer_packs.id", ondelete="CASCADE"))
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"))
    answer_packs = relationship("AnswerPack", back_populates="chats")
    chats = relationship("Chat", back_populates="answer_packs")
