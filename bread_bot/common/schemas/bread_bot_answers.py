from typing import Optional, Union

from pydantic import BaseModel


class BaseAnswerSchema(BaseModel):
    reply_to_message_id: Optional[int] = None
    chat_id: int

    def send_body(self):
        return self.dict(exclude_none=True)


class TextAnswerSchema(BaseAnswerSchema):
    text: str


class VoiceAnswerSchema(BaseAnswerSchema):
    voice: str


class PhotoAnswerSchema(BaseAnswerSchema):
    photo: str
    caption: str | None = None


class StickerAnswerSchema(BaseAnswerSchema):
    sticker: str


class GifAnswerSchema(BaseAnswerSchema):
    animation: str


class VideoAnswerSchema(BaseAnswerSchema):
    video: str


class VideoNoteAnswerSchema(BaseAnswerSchema):
    video_note: str
