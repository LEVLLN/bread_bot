from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from bread_bot.common.models.answer_entities.base_answer_entities import BaseEntity


class VideoEntity(BaseEntity):
    __tablename__ = "video_entities"
    pack_id = Column(
        Integer,
        ForeignKey("answer_packs.id", ondelete="CASCADE"),
    )

    answer_packs = relationship("AnswerPack", back_populates="video_entities")
