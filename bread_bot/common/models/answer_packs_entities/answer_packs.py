from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, and_, SmallInteger
from sqlalchemy.orm import relationship

from bread_bot.common.models.answer_packs_entities.answer_packs_to_chats import AnswerPacksToChats
from bread_bot.main.database import mixins


class AnswerPack(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "answer_packs"

    name = Column(String(255), nullable=False, default="based")
    is_private = Column(Boolean, nullable=False, default=True)
    author = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    answer_chance = Column(SmallInteger, default=100, nullable=False)

    chats = relationship("AnswerPacksToChats", back_populates="answer_packs")
    answer_entities = relationship("AnswerEntity", back_populates="answer_packs")

    @classmethod
    async def get_by_chat_id(cls, db, chat_id: int):
        answer_chat = await AnswerPacksToChats.async_first(db=db, where=AnswerPacksToChats.chat_id == chat_id)
        if answer_chat:
            answer_pack = await AnswerPack.async_first(
                db=db,
                where=and_(
                    AnswerPack.name == "based", AnswerPack.is_private == True, AnswerPack.id == answer_chat.pack_id
                ),
            )
            return answer_pack
        else:
            return None

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
