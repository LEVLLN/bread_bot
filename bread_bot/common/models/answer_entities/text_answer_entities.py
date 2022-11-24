from sqlalchemy import ForeignKey, Integer, Column
from sqlalchemy.orm import relationship

from bread_bot.common.models.answer_entities.base_answer_entities import BaseEntity


class TextEntity(BaseEntity):
    __tablename__ = 'text_entities'
    pack_id = Column(
        Integer,
        ForeignKey('answer_packs.id', ondelete='CASCADE'),
    )

    answer_packs = relationship('AnswerPack', back_populates='text_entities')
