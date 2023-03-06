from bread_bot.common.exceptions.base import NextStepException, RaiseUpException
from bread_bot.common.schemas.telegram_messages import StandardBodySchema, MessageSchema, BaseMessageSchema
from bread_bot.common.utils.structs import AnswerEntityContentTypesEnum


class MessageService(object):
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
    def select_content_from_message(
        cls, message: BaseMessageSchema
    ) -> tuple[str, AnswerEntityContentTypesEnum, str | None]:
        description = None
        if message.voice:
            value = message.voice.file_id
            content_type = AnswerEntityContentTypesEnum.VOICE
        elif message.photo:
            value = message.photo[0].file_id
            description = message.caption
            content_type = AnswerEntityContentTypesEnum.PICTURE
        elif message.sticker:
            value = message.sticker.file_id
            content_type = AnswerEntityContentTypesEnum.STICKER
        elif message.video:
            value = message.video.file_id
            content_type = AnswerEntityContentTypesEnum.VIDEO
        elif message.video_note:
            value = message.video_note.file_id
            content_type = AnswerEntityContentTypesEnum.VIDEO_NOTE
        elif message.animation:
            value = message.animation.file_id
            content_type = AnswerEntityContentTypesEnum.ANIMATION
        elif message.text:
            value = message.text
            content_type = AnswerEntityContentTypesEnum.TEXT
        else:
            raise RaiseUpException("Данный тип данных не поддерживается")
        return value, content_type, description
