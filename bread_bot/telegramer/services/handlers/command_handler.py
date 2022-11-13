from bread_bot.telegramer.exceptions.base import NextStepException
from bread_bot.telegramer.schemas.bread_bot_answers import BaseAnswerSchema, TextAnswerSchema
from bread_bot.telegramer.services.commands.command_parser import CommandParser
from bread_bot.telegramer.services.handlers.handler import AbstractHandler
from bread_bot.telegramer.services.handlers.methods.admin_commands import AdminCommandMethod
from bread_bot.telegramer.utils.structs import (
    AdminCommandsEnum,
    MemberCommandsEnum,
    EntertainmentCommandsEnum,
)


class CommandHandler(AbstractHandler):
    async def condition(self) -> bool:
        return (self.message_service
                and self.message_service.message
                and self.message_service.message.text)

    async def process(self) -> BaseAnswerSchema:
        if not self.condition():
            raise NextStepException("Не подходит условие для обработки")
        command_instance = CommandParser(message_text=self.message_service.message.text).parse()
        match command_instance.command:
            case AdminCommandsEnum():
                return await AdminCommandMethod(
                    db=self.db,
                    message_service=self.message_service,
                    member_service=self.member_service,
                    command_instance=command_instance,
                ).execute()
            case EntertainmentCommandsEnum():
                return TextAnswerSchema(
                    text="Результат команды",
                    reply_to_message_id=None,
                    chat_id=1,
                )
            case MemberCommandsEnum():
                return BaseAnswerSchema(chat_id=1)
            case _:
                raise NextStepException("Переход на следующий шаг")
