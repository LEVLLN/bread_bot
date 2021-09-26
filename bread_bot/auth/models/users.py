from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from bread_bot.main.database import mixins


class User(mixins.AbstractIsActiveBaseModel,
           mixins.BaseModel,
           mixins.CRUDMixin):
    __tablename__ = 'users'
    username = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255))
    surname = Column(String(255))
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    @classmethod
    def get_user(cls, db: Session, username: str) -> 'User':
        return cls.first(db, **{'username': username})
