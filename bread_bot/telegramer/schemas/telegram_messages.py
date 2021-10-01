from typing import Optional, List

from pydantic import BaseModel, Field


class MemberSchema(BaseModel):
    id: Optional[int] = None
    is_bot: bool
    username: Optional[str] = ''
    last_name: Optional[str] = ''
    first_name: Optional[str] = ''


class ChatSchema(BaseModel):
    id: int
    title: Optional[str] = None
    type: Optional[str] = None


class MessageSchema(BaseModel):
    message_id: int
    source: MemberSchema = Field(..., alias='from')
    chat: ChatSchema
    date: Optional[int] = None
    text: Optional[str] = ''

    class Config:
        allow_population_by_field_name = True


class StandardBodySchema(BaseModel):
    update_id: int
    message: Optional[MessageSchema] = None
    edited_message: Optional[MessageSchema] = None


class MemberListSchema(BaseModel):
    user: Optional[MemberSchema] = None


class ChatMemberBodySchema(BaseModel):
    result: List[MemberListSchema] = []


class GetWebHookInfoResultSchema(BaseModel):
    url: str


class GetWebHookInfoSchema(BaseModel):
    ok: bool
    result: GetWebHookInfoResultSchema
