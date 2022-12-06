from sqlalchemy import ForeignKey, Integer, Column, Text
from sqlalchemy.orm import relationship

from bread_bot.common.models.answer_entities.base_answer_entities import BaseEntity


class PhotoEntity(BaseEntity):
    __tablename__ = "photo_entities"
    pack_id = Column(
        Integer,
        ForeignKey("answer_packs.id", ondelete="CASCADE"),
    )
    description = Column(Text, nullable=True)

    answer_packs = relationship("AnswerPack", back_populates="photo_entities")
