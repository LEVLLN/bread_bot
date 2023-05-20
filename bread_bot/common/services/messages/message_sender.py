import logging

from bread_bot.common.clients.telegram_client import TelegramClient
from bread_bot.common.schemas.bread_bot_answers import (
    BaseAnswerSchema,
    GifAnswerSchema,
    PhotoAnswerSchema,
    StickerAnswerSchema,
    TextAnswerSchema,
    VideoAnswerSchema,
    VideoNoteAnswerSchema,
    VoiceAnswerSchema,
)
from bread_bot.main.settings import MESSAGE_LEN_LIMIT
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
            return [
                message,
            ]

    def _fit_in_messages(self) -> list[TextAnswerSchema]:
        """
        thx for Roman Kitaev for this code
        """
        lines = self.message.text.splitlines(keepends=1)
        messages = [[]]
        for line in lines:
            offset = 0
            while True:
                chunk = line[offset : MESSAGE_LEN_LIMIT + offset]
                offset += MESSAGE_LEN_LIMIT
                if not chunk:
                    break
                if sum(len(x) for x in messages[-1]) + len(chunk) > MESSAGE_LEN_LIMIT:
                    messages.append([])
                messages[-1].append(chunk)
        return [
            TextAnswerSchema(
                text="".join(lines),
                chat_id=self.message.chat_id,
                reply_to_message_id=self.message.reply_to_message_id,
            )
            for lines in messages
            if lines
        ]

    async def send_messages_to_chat(self):
        """Отправка сообщения в чат"""
        if not self.message:
            return None
        messages = [
            self.message,
        ]
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
                messages = self._fit_in_messages()
            case _:
                logger.error("Unknown type to send of obj: %s", self.message)
                return None
        for message in messages:
            await self.telegram_client.send(
                data=message.send_body(),
                method=method,
            )
