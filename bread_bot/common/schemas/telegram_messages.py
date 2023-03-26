
from pydantic import BaseModel, Field


class MemberSchema(BaseModel):
    id: int
    is_bot: bool
    username: str | None = ""
    last_name: str | None = ""
    first_name: str | None = ""


class ChatSchema(BaseModel):
    id: int
    title: str | None = None
    type: str | None = None


class VoiceSchema(BaseModel):
    duration: int | None
    mime_type: str | None
    file_id: str | None


class PhotoSchema(BaseModel):
    file_id: str | None


class StickerSchema(BaseModel):
    file_id: str | None


class GifSchema(BaseModel):
    file_id: str | None


class VideoSchema(BaseModel):
    file_id: str | None


class VideoNoteSchema(BaseModel):
    file_id: str | None


class BaseMessageSchema(BaseModel):
    message_id: int
    source: MemberSchema = Field(..., alias="from")
    chat: ChatSchema
    date: int | None = None
    text: str | None = ""
    voice: VoiceSchema | None = None
    photo: list[PhotoSchema] = []
    sticker: StickerSchema | None = None
    caption: str | None = None
    animation: GifSchema | None = None
    video: VideoSchema | None = None
    video_note: VideoNoteSchema | None = None


class MessageSchema(BaseMessageSchema):
    reply: BaseMessageSchema | None = Field(None, alias="reply_to_message")

    class Config:
        allow_population_by_field_name = True


class StandardBodySchema(BaseModel):
    update_id: int
    message: MessageSchema | None = None
    edited_message: MessageSchema | None = None


class MemberListSchema(BaseModel):
    user: MemberSchema | None = None


class ChatMemberBodySchema(BaseModel):
    result: list[MemberListSchema] = []


class GetWebHookInfoResultSchema(BaseModel):
    url: str


class GetWebHookInfoSchema(BaseModel):
    ok: bool
    result: GetWebHookInfoResultSchema
