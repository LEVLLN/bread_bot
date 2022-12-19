from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from bread_bot.common.utils.structs import AnswerEntityTypesEnum, AnswerEntityContentTypesEnum
from bread_bot.main.database import mixins


class AnswerEntity(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "answer_entities"

    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    reaction_type = Column(Enum(AnswerEntityTypesEnum), nullable=False)
    content_type = Column(Enum(AnswerEntityContentTypesEnum), nullable=False)
    description = Column(Text, nullable=True)
    pack_id = Column(
        Integer,
        ForeignKey("answer_packs.id", ondelete="CASCADE"),
    )

    answer_packs = relationship("AnswerPack", back_populates="gif_entities")

    def __repr__(self):
        return (
            f"{self.__class__.__name__} "
            f"type: {self.reaction_type} "
            f"content_type: {self.content_type} "
            f"key: '{self.key}', "
            f"value: '{self.value}', "
            f"pack_id: {self.pack_id}>"
        )
