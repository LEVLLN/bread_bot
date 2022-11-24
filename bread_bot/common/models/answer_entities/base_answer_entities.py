from sqlalchemy import Column, String, Text, Enum

from bread_bot.main.database import mixins
from bread_bot.common.utils.structs import AnswerEntityTypesEnum


class BaseEntity(mixins.AbstractIsActiveBaseModel,
                 mixins.BaseModel,
                 mixins.CRUDMixin):
    __abstract__ = True

    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    reaction_type = Column(Enum(AnswerEntityTypesEnum), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"<[{self.reaction_type}] " \
               f"key: '{self.key}', " \
               f"value: '{self.value}', " \
               f"pack_id: {self.pack_id}>"
