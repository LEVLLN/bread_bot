import logging

from httpx import Response

from bread_bot.common.schemas.bread_bot_answers import (
    BaseAnswerSchema,
    VoiceAnswerSchema,
    PhotoAnswerSchema,
    TextAnswerSchema,
    StickerAnswerSchema,
)
from bread_bot.common.schemas.telegram_messages import (
    ChatMemberBodySchema,
    GetWebHookInfoSchema,
)
from bread_bot.main import settings
from bread_bot.main.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class TelegramClient(BaseHTTPClient):
    def __init__(self):
        self.send_video = "sendVideo"
        self.send_video_note = "sendVideoNote"
        self.send_animation = "sendAnimation"
        self.send_message_method = "sendMessage"
        self.send_voice_method = "sendVoice"
        self.send_photo_method = "sendPhoto"
        self.send_sticker_method = "sendSticker"
        self.set_webhook_method = "setWebhook"
        self.get_webhook_info_method = "getWebhookInfo"
        self.get_chat_method = "getChatAdministrators"
        self.base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
        self.headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
        }

    async def send_message(self, chat_id: int, message: str, reply_to: int = None) -> Response:
        data = {
            "chat_id": chat_id,
            "text": message,
        }
        if reply_to is not None:
            data["reply_to_message_id"] = reply_to

        return await self.request(
            method="POST",
            url=f"{self.base_url}/{self.send_message_method}",
            data=data,
            headers=self.headers,
        )

    async def send_message_by_schema(self, schema: BaseAnswerSchema):
        match schema:
            case VoiceAnswerSchema():
                method = self.send_voice_method
            case PhotoAnswerSchema():
                method = self.send_photo_method
            case StickerAnswerSchema():
                method = self.send_sticker_method
            case TextAnswerSchema():
                method = self.send_message_method
            case _:
                logger.error("Unknown type to send of obj: %s", schema)
                return None

        return await self.request(
            method="POST",
            url=f"{self.base_url}/{method}",
            data=schema.send_body(),
            headers=self.headers,
        )

    async def set_webhook(self) -> bool:
        response = await self.request(
            method="POST",
            url=f"{self.base_url}/{self.set_webhook_method}",
            data={"url": settings.NGROK_HOST},
            headers=self.headers,
        )
        if response.status_code != 200 or not response.json().get("ok"):
            return False
        return True

    async def get_webhook_info(self) -> GetWebHookInfoSchema:
        response = await self.request(
            method="POST",
            url=f"{self.base_url}/{self.get_webhook_info_method}",
            data={},
            headers=self.headers,
        )
        result = response.json()
        if response.status_code != 200 or not result.get("ok"):
            raise ValueError("Ошибка получения информации по webhook")
        return GetWebHookInfoSchema(**result)

    async def compare_webhooks(self) -> bool:
        webhook = await self.get_webhook_info()
        return settings.NGROK_HOST == webhook.result.url

    async def get_chat(self, chat_id) -> ChatMemberBodySchema:
        response = await self.request(
            method="POST",
            url=f"{self.base_url}/{self.get_chat_method}",
            data={"chat_id": chat_id},
            headers=self.headers,
        )
        result = response.json()
        if response.status_code != 200 or not result.get("ok") or "result" not in result:
            raise ValueError("Ошибка получения администраторов чата")
        return ChatMemberBodySchema(**result)

    async def send(self, data: dict, method: str):
        return await self.request(
            method="POST",
            url=f"{self.base_url}/{method}",
            data=data,
            headers=self.headers,
        )
