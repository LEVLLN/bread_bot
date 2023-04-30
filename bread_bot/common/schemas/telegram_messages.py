from typing import Optional, List

from pydantic import BaseModel, Field


class MemberSchema(BaseModel):
    id: int
    is_bot: bool
    username: Optional[str] = ""
    last_name: Optional[str] = ""
    first_name: Optional[str] = ""


class ChatSchema(BaseModel):
    id: int
    title: Optional[str] = None
    type: Optional[str] = None


class VoiceSchema(BaseModel):
    duration: Optional[int]
    mime_type: Optional[str]
    file_id: str | None = None
    file_unique_id: str | None = None


class PhotoSchema(BaseModel):
    file_id: str | None = None
    file_unique_id: str | None = None


class StickerSchema(BaseModel):
    file_id: str | None = None
    file_unique_id: str | None = None


class GifSchema(BaseModel):
    file_id: str | None = None
    file_unique_id: str | None = None


class VideoSchema(BaseModel):
    file_id: str | None = None
    file_unique_id: str | None = None


class VideoNoteSchema(BaseModel):
    file_id: str | None = None
    file_unique_id: str | None = None


class BaseMessageSchema(BaseModel):
    message_id: int
    source: MemberSchema = Field(..., alias="from")
    chat: ChatSchema
    date: Optional[int] = None
    text: Optional[str] = ""
    voice: Optional[VoiceSchema] = None
    photo: List[PhotoSchema] = []
    sticker: Optional[StickerSchema] = None
    caption: Optional[str] = None
    animation: Optional[GifSchema] = None
    video: Optional[VideoSchema] = None
    video_note: Optional[VideoNoteSchema] = None


class MessageSchema(BaseMessageSchema):
    reply: Optional[BaseMessageSchema] = Field(None, alias="reply_to_message")

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
