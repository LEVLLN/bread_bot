from typing import Any

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
        select_in_loads = [
            cls.text_entities,
            cls.sticker_entities,
            cls.voice_entities,
            cls.photo_entities,
            cls.gif_entities,
            cls.video_entities,
            cls.video_note_entities,
        ]
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

    @classmethod
    async def get_or_create_by_chat_id(cls, db, chat_id: int):
        answer_pack = await cls.get_by_chat_id(
            db=db,
            chat_id=chat_id,
            select_in_loads=[
                AnswerPack.text_entities,
                AnswerPack.sticker_entities,
                AnswerPack.voice_entities,
                AnswerPack.photo_entities,
                AnswerPack.gif_entities,
                AnswerPack.video_entities,
                AnswerPack.video_note_entities,
            ],
        )
        if answer_pack is None:
            answer_pack = await cls.create_by_chat_id(db=db, chat_id=chat_id)
        return answer_pack

    def get_keys(self, reaction_type: str) -> dict[str, Any]:
        answer_pack_by_keys = {}
        entities = (
            self.text_entities
            + self.sticker_entities
            + self.photo_entities
            + self.voice_entities
            + self.gif_entities
            + self.video_entities
            + self.video_note_entities
        )
        for entity in entities:
            if entity.reaction_type != reaction_type:
                continue
            if entity.key not in answer_pack_by_keys:
                answer_pack_by_keys[entity.key] = [
                    entity,
                ]
                continue
            answer_pack_by_keys[entity.key].append(entity)
        return answer_pack_by_keys
