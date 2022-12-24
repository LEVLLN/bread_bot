from sqlalchemy import Column, String, Boolean, BigInteger
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins


class Member(mixins.AbstractIsActiveBaseModel, mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "members"

    member_id = Column(BigInteger, nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_bot = Column(Boolean, default=False)

    chats = relationship("ChatToMember", back_populates="member")
