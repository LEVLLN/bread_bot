from sqlalchemy import ForeignKey, Integer, Column
from sqlalchemy.orm import relationship

from bread_bot.telegramer.models.answer_entities.base_answer_entities import BaseEntity


class VoiceEntity(BaseEntity):
    __tablename__ = 'voice_entities'
    pack_id = Column(
        Integer,
        ForeignKey('answer_packs.id', ondelete='CASCADE'),
    )

    answer_packs = relationship('AnswerPack', back_populates='voice_entities')
