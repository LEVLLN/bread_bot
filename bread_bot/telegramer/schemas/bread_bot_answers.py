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
    voice_file_id: str
