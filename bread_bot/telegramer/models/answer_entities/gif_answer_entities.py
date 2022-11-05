from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from bread_bot.telegramer.models.answer_entities.base_answer_entities import BaseEntity


class GifEntity(BaseEntity):
    __tablename__ = 'gif_entities'
    pack_id = Column(
        Integer,
        ForeignKey('answer_packs.id', ondelete='CASCADE'),
    )

    answer_packs = relationship('AnswerPack', back_populates='gif_entities')
