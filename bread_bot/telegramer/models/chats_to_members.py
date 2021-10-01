from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from bread_bot.main.database import mixins


class ChatToMember(mixins.AbstractIsActiveBaseModel,
                   mixins.BaseModel,
                   mixins.CRUDMixin):
    __tablename__ = 'chats_to_members'

    member_id = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'))
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    member = relationship("Member", back_populates="chats")
    chat = relationship("Chat", back_populates="members")
