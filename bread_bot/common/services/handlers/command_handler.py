from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.schemas.bread_bot_answers import BaseAnswerSchema, TextAnswerSchema
from bread_bot.common.services.commands.command_parser import CommandParser
from bread_bot.common.services.handlers.command_methods.entertainment_command_method import EntertainmentCommandMethod
from bread_bot.common.services.handlers.command_methods.integration_command_method import IntegrationCommandMethod
from bread_bot.common.services.handlers.command_methods.member_command_method import MemberCommandMethod
from bread_bot.common.services.handlers.handler import AbstractHandler
from bread_bot.common.services.handlers.command_methods.admin_command_method import AdminCommandMethod
from bread_bot.common.utils.structs import (
    AdminCommandsEnum,
    MemberCommandsEnum,
    EntertainmentCommandsEnum,
    IntegrationCommandsEnum,
)


class CommandHandler(AbstractHandler):
    async def condition(self) -> bool:
        return self.message_service and self.message_service.message and self.message_service.message.text

    async def process(self) -> BaseAnswerSchema:
        if not await self.condition():
            raise NextStepException("Не подходит условие для обработки")
        command_instance = CommandParser(message_text=self.message_service.message.text).parse()
        command_params = dict(
            db=self.db,
            message_service=self.message_service,
            member_service=self.member_service,
            command_instance=command_instance,
        )
        match command_instance.command:
            case AdminCommandsEnum():
                return await AdminCommandMethod(**command_params).execute()
            case EntertainmentCommandsEnum():
                return await EntertainmentCommandMethod(**command_params).execute()
            case MemberCommandsEnum():
                return await MemberCommandMethod(**command_params).execute()
            case IntegrationCommandsEnum():
                return await IntegrationCommandMethod(**command_params).execute()
            case _:
                raise NextStepException("Переход на следующий шаг")
