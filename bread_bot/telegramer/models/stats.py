from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins


class Stats(mixins.AbstractIsActiveBaseModel,
            mixins.BaseModel,
            mixins.CRUDMixin):
    __tablename__ = 'stats'

    member_id = Column(Integer, ForeignKey('members.id'))
    slug = Column(String(255), nullable=False)
    count = Column(BigInteger, default=0, nullable=False)
    member = relationship('Member', back_populates='stats')
    chat_id = Column(BigInteger, nullable=True)
