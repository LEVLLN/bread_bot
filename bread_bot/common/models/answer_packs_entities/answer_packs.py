from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, select, and_, SmallInteger
from sqlalchemy.orm import relationship, selectinload

from bread_bot.common.models.answer_packs_entities.answer_packs_to_chats import AnswerPacksToChats
from bread_bot.main.database import mixins


class AnswerPack(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "answer_packs"

    name = Column(String(255), nullable=False, default="based")
    is_private = Column(Boolean, nullable=False, default=True)
    author = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    answer_chance = Column(SmallInteger, default=100, nullable=False)

    chats = relationship("AnswerPacksToChats", back_populates="answer_packs")
    gif_entities = relationship("GifEntity", back_populates="answer_packs")
    photo_entities = relationship("PhotoEntity", back_populates="answer_packs")
    sticker_entities = relationship("StickerEntity", back_populates="answer_packs")
    text_entities = relationship("TextEntity", back_populates="answer_packs")
    voice_entities = relationship("VoiceEntity", back_populates="answer_packs")
    video_entities = relationship("VideoEntity", back_populates="answer_packs")
    video_note_entities = relationship("VideoNoteEntity", back_populates="answer_packs")

    @classmethod
    async def get_by_chat_id(cls, db, chat_id: int, select_in_loads: list = None):
        statement = (
            select(AnswerPack)
            .where(and_(AnswerPack.name == "based", AnswerPack.is_private == True))
            .join(AnswerPacksToChats)
            .where(AnswerPacksToChats.chat_id == chat_id)
        )
        if select_in_loads is not None:
            for sil in select_in_loads:
                statement = statement.options(selectinload(sil))
        async with db as session:
            answer_packs_qs = await session.execute(statement)
            return answer_packs_qs.scalars().first()

    @classmethod
    async def create_by_chat_id(cls, db, chat_id: int):
        answer_pack = await AnswerPack.async_add(db=db, instance=AnswerPack())
        await AnswerPacksToChats.async_add(
            db=db,
            instance=AnswerPacksToChats(
                pack_id=answer_pack.id,
                chat_id=chat_id,
            ),
        )
        return answer_pack
