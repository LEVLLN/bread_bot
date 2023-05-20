from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins


class DictionaryEntity(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "dictionary_entities"

    value = Column(Text, nullable=False)
    chat_id = Column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
    )

    chats = relationship("Chat", back_populates="dictionary_entities")
