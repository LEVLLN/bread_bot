from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from bread_bot.common.utils.structs import AnswerEntityReactionTypesEnum, AnswerEntityContentTypesEnum
from bread_bot.main.database import mixins


class AnswerEntity(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "answer_entities"

    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    file_unique_id = Column(String(255), nullable=True)
    reaction_type = Column(Enum(AnswerEntityReactionTypesEnum), nullable=False)
    content_type = Column(Enum(AnswerEntityContentTypesEnum), nullable=False)
    description = Column(Text, nullable=True)
    pack_id = Column(
        Integer,
        ForeignKey("answer_packs.id", ondelete="CASCADE"),
    )

    answer_packs = relationship("AnswerPack", back_populates="answer_entities")

    def __repr__(self):
        return (
            f"{self.__class__.__name__} "
            f"type: {self.reaction_type} "
            f"content_type: {self.content_type} "
            f"key: '{self.key}', "
            f"value: '{self.value}', "
            f"pack_id: {self.pack_id}>"
        )

    @classmethod
    async def get_keys(cls, db: AsyncSession, pack_id: int, reaction_type: AnswerEntityReactionTypesEnum):
        statement = (
            select(cls.key)
            .where(
                and_(
                    cls.reaction_type == reaction_type,
                    cls.pack_id == pack_id,
                )
            )
            .distinct(cls.key)
        )
        result = await db.execute(statement)
        return result.scalars().all()
