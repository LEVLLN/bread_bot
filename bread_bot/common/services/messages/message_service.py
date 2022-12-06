from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.schemas.telegram_messages import StandardBodySchema, MessageSchema


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
