from sqlalchemy import Column, JSON, String

from bread_bot.main.database import mixins


class Property(mixins.AbstractIsActiveBaseModel,
               mixins.BaseModel,
               mixins.CRUDMixin):
    __tablename__ = 'properties'
    slug = Column(String(255), nullable=False)
    data = Column(JSON, default=JSON.NULL, nullable=True)
