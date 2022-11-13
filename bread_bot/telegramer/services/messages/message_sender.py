import asyncio

from bread_bot.main.settings import MESSAGE_LEN_LIMIT
from bread_bot.telegramer.clients.telegram_client import TelegramClient
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema, BaseAnswerSchema
from bread_bot.utils.helpers import chunks


class MessageSender:
    """Сервис отправки сообщений"""

    def __init__(self, message: BaseAnswerSchema):
        self.message: BaseAnswerSchema = message

    def send_messages_to_chat(self):
        telegram_client = TelegramClient()
        message_parts = []
        # Если сообщение очень длинное для текстового формата - бьем на чанки и выполняем асинхронную отправку
        if isinstance(self.message, TextAnswerSchema) and self.message.text and len(self.message.text) > \
                MESSAGE_LEN_LIMIT:
            for chunk in chunks(self.message.text, MESSAGE_LEN_LIMIT):
                message_parts.append(
                    TextAnswerSchema(
                        text=chunk,
                        chat_id=self.message.chat_id,
                        reply_to_message_id=self.message.reply_to_message_id,
                    )
                )
            if len(message_parts) > 0:
                await asyncio.gather(*[
                    telegram_client.send_message_by_schema(message_part) for message_part in message_parts
                ])
            return
        else:
            await telegram_client.send_message_by_schema(self.message)
