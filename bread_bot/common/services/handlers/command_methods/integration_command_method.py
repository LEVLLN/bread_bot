from bread_bot.common.clients.baneks_client import BaneksClient
from bread_bot.common.clients.evil_insult_client import EvilInsultClient
from bread_bot.common.clients.forismatic_client import ForismaticClient
from bread_bot.common.clients.great_advice import GreatAdviceClient
from bread_bot.common.exceptions.base import NextStepException, RaiseUpException
from bread_bot.common.services.handlers.command_methods.base_command_method import BaseCommandMethod
from bread_bot.common.utils.structs import IntegrationCommandsEnum


class IntegrationCommandMethod(BaseCommandMethod):
    async def execute(self):
        match self.command_instance.command:
            case IntegrationCommandsEnum.ADVICE:
                return await self.get_advice()
            case IntegrationCommandsEnum.QUOTE:
                return await self.get_quote()
            case IntegrationCommandsEnum.INSULT:
                return await self.get_insult()
            case IntegrationCommandsEnum.JOKE:
                return await self.get_joke()
            case _:
                NextStepException("Не найдена команда")

    async def get_advice(self):
        advice = await GreatAdviceClient().get_advice()
        return super()._return_answer(advice.text)

    async def get_quote(self):
        quote = await ForismaticClient().get_quote_text()
        return super()._return_answer(f"{quote.text}\n\n© {quote.author}")

    async def get_insult(self):
        username = None
        if self.message_service.message.reply:
            username = f"@{self.member_service.message.reply.source.username}"
        evil_insult = await EvilInsultClient().get_evil_insult()
        insult = f"{evil_insult.insult}\n\n© {evil_insult.comment}"
        if username:
            return super()._return_answer(f"{username}\n{insult}")
        return super()._return_answer(insult)

    async def get_joke(self):
        joke_vendor = BaneksClient()
        text = await joke_vendor.get_text()

        if text is None:
            raise RaiseUpException("Не получилось получить анекдот у поставщика")
        return super()._return_answer(f"{text}\n\n© {joke_vendor.url}")
