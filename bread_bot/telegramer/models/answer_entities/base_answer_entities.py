from sqlalchemy import Column, String, Text, Enum

from bread_bot.main.database import mixins
from bread_bot.telegramer.utils.structs import AnswerEntityTypesEnum


class BaseEntity(mixins.AbstractIsActiveBaseModel,
                 mixins.BaseModel,
                 mixins.CRUDMixin):
    __abstract__ = True

    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    reaction_type = Column(Enum(AnswerEntityTypesEnum), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}[key: '{self.key}', value: '{self.value}', pack_id: {self.pack_id}]"
