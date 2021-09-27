from typing import Dict, List, Union

from pydantic import BaseModel

from bread_bot.telegramer.schemas.telegram_messages import MemberSchema


class LocalMemeSchema(BaseModel):
    type: str
    chat_id: int
    data: Union[Dict, List]


class SendMessageSchema(BaseModel):
    chat_id: int
    message: str


class ChatSchema(BaseModel):
    chat_id: int
    name: str

    class Config:
        orm_mode = True


class MemberDBSchema(MemberSchema):
    class Config:
        orm_mode = True
