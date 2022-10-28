from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins


class AnswerPack(mixins.AbstractIsActiveBaseModel,
                 mixins.BaseModel,
                 mixins.CRUDMixin):
    __tablename__ = 'answer_packs'

    name = Column(String(255), nullable=False, default="based")
    is_private = Column(Boolean, nullable=False, default=True)
    author = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=True)

    chats = relationship(
        "AnswerPacksToChats",
        back_populates="answer_packs")
    gif_entities = relationship(
        "GifEntity",
        back_populates="answer_packs"
    )
    photo_entities = relationship(
        "PhotoEntity",
        back_populates="answer_packs"
    )
    sticker_entities = relationship(
        "StickerEntity",
        back_populates="answer_packs"
    )
    text_entities = relationship(
        "TextEntity",
        back_populates="answer_packs"
    )
    voice_entities = relationship(
        "VoiceEntity",
        back_populates="answer_packs"
    )
