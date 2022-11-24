import logging

from bread_bot.main.settings import MESSAGE_LEN_LIMIT
from bread_bot.common.clients.telegram_client import TelegramClient
from bread_bot.common.schemas.bread_bot_answers import (
    TextAnswerSchema, BaseAnswerSchema, VoiceAnswerSchema,
    PhotoAnswerSchema, StickerAnswerSchema, GifAnswerSchema,
    VideoAnswerSchema, VideoNoteAnswerSchema,
)
from bread_bot.utils.helpers import chunks

logger = logging.getLogger(__name__)


class MessageSender:
    """Сервис отправки сообщений"""
    def __init__(self, message: BaseAnswerSchema):
        self.message: BaseAnswerSchema = message
        self.telegram_client: TelegramClient = TelegramClient()

    @staticmethod
    def _split_text_messages(message: BaseAnswerSchema | TextAnswerSchema) -> list[TextAnswerSchema]:
        """
            У одного сообщения есть лимит по символам
            Если сообщение превышает лимит - необходимо его разделить на несколько сообщений
        """
        result = []
        if len(message.text) > MESSAGE_LEN_LIMIT:
            for chunk in chunks(message.text, MESSAGE_LEN_LIMIT):
                result.append(
                    TextAnswerSchema(
                        text=chunk,
                        chat_id=message.chat_id,
                        reply_to_message_id=message.reply_to_message_id,
                    )
                )
            return result
        else:
            return [message, ]

    async def send_messages_to_chat(self):
        """Отправка сообщения в чат"""
        messages = [self.message, ]
        match self.message:
            case VoiceAnswerSchema():
                method = self.telegram_client.send_voice_method
            case PhotoAnswerSchema():
                method = self.telegram_client.send_photo_method
            case StickerAnswerSchema():
                method = self.telegram_client.send_sticker_method
            case GifAnswerSchema():
                method = self.telegram_client.send_animation
            case VideoAnswerSchema():
                method = self.telegram_client.send_video
            case VideoNoteAnswerSchema():
                method = self.telegram_client.send_video_note
            case TextAnswerSchema():
                method = self.telegram_client.send_message_method
                messages = self._split_text_messages(self.message)
            case _:
                logger.error("Unknown type to send of obj: %s", self.message)
                return None
        for message in messages:
            await self.telegram_client.send(
                data=message.send_body(),
                method=method,
            )
