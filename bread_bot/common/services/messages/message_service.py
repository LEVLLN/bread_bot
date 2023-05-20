from pydantic import BaseModel

from bread_bot.common.exceptions.base import NextStepException, RaiseUpException
from bread_bot.common.schemas.telegram_messages import BaseMessageSchema, MessageSchema, StandardBodySchema
from bread_bot.common.utils.structs import AnswerEntityContentTypesEnum


class Content(BaseModel):
    value: str
    content_type: AnswerEntityContentTypesEnum
    caption: str | None = None
    file_unique_id: str | None = None


class MessageService:
    """Сервис сообщений"""

    def __init__(
        self,
        request_body: StandardBodySchema = None,
    ):
        self.request_body: StandardBodySchema = request_body
        self.message = self.get_message()

    @property
    def has_message(self) -> bool:
        """Проверка тела запроса на наличие сообщения"""
        return hasattr(self.request_body, "message") and self.request_body.message is not None

    @property
    def has_edited_message(self) -> bool:
        """Проверка тела запроса на наличие отредактированного сообщения"""
        return hasattr(self.request_body, "edited_message") and self.request_body.edited_message is not None

    def get_message(self) -> MessageSchema:
        """Получение редактированного или обычного сообщения в качестве основного"""
        if not self.has_message and not self.has_edited_message:
            raise NextStepException("Отсутствует сообщение")
        if self.has_edited_message:
            return self.request_body.edited_message
        else:
            return self.request_body.message

    @classmethod
    def select_content_from_message(cls, message: BaseMessageSchema) -> Content:
        if message.voice:
            return Content(
                value=message.voice.file_id,
                file_unique_id=message.voice.file_unique_id,
                content_type=AnswerEntityContentTypesEnum.VOICE,
            )
        elif message.photo:
            return Content(
                value=message.photo[0].file_id,
                file_unique_id=message.photo[0].file_unique_id,
                caption=message.caption,
                content_type=AnswerEntityContentTypesEnum.PICTURE,
            )
        elif message.sticker:
            return Content(
                value=message.sticker.file_id,
                file_unique_id=message.sticker.file_unique_id,
                content_type=AnswerEntityContentTypesEnum.STICKER,
            )
        elif message.video:
            return Content(
                value=message.video.file_id,
                file_unique_id=message.video.file_unique_id,
                caption=message.caption,
                content_type=AnswerEntityContentTypesEnum.VIDEO,
            )
        elif message.video_note:
            return Content(
                value=message.video_note.file_id,
                file_unique_id=message.video_note.file_unique_id,
                content_type=AnswerEntityContentTypesEnum.VIDEO_NOTE,
            )
        elif message.animation:
            return Content(
                value=message.animation.file_id,
                file_unique_id=message.animation.file_unique_id,
                content_type=AnswerEntityContentTypesEnum.ANIMATION,
            )
        elif message.text:
            return Content(
                value=message.text,
                content_type=AnswerEntityContentTypesEnum.TEXT,
            )
        else:
            raise RaiseUpException("Данный тип данных не поддерживается")
