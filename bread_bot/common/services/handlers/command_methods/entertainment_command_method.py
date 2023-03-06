import datetime
import math
import random

from sqlalchemy import select, and_

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.models import AnswerPack, AnswerEntity
from bread_bot.common.schemas.telegram_messages import BaseMessageSchema
from bread_bot.common.services.commands.command_settings import CommandSettings
from bread_bot.common.services.handlers.command_methods.base_command_method import BaseCommandMethod
from bread_bot.common.utils.structs import (
    ALTER_NAMES,
    BOT_NAME,
    EntertainmentCommandsEnum,
    AnswerEntityContentTypesEnum,
)


class EntertainmentCommandMethod(BaseCommandMethod):
    async def execute(self):
        match self.command_instance.command:
            case EntertainmentCommandsEnum.CHANCE:
                return self.get_chance()
            case EntertainmentCommandsEnum.CHOOSE_VARIANT:
                return self.choose_variant()
            case EntertainmentCommandsEnum.RANDOM:
                return self.get_random()
            case EntertainmentCommandsEnum.HELP:
                return self.help()
            case EntertainmentCommandsEnum.PAST_DATE:
                return self.get_date(future=False)
            case EntertainmentCommandsEnum.FUTURE_DATE:
                return self.get_date(future=True)
            case EntertainmentCommandsEnum.HOW_MANY:
                return self.get_how_many()
            case EntertainmentCommandsEnum.REGENERATE_MESSAGE:
                return await self.regenerate_message()
            case _:
                raise NextStepException("Не найдена команде")

    def get_chance(self):
        return super()._return_answer(
            f"Есть вероятность {self.command_instance.rest_text} - {str(random.randint(0, 100))}%"
        )

    def choose_variant(self):
        return super()._return_answer(random.choice(self.command_instance.value_list).strip())

    def get_random(self):
        return super()._return_answer(str(random.randint(0, 10000)))

    def get_how_many(self):
        rest_text = self.command_instance.rest_text.replace("?", "")
        return super()._return_answer(f"{rest_text} - {str(random.randint(0, 1000))}")

    def get_date(self, future: bool = True):
        rest_text = self.command_instance.rest_text.replace("?", "")
        today = datetime.datetime.today()
        delta = datetime.timedelta(
            days=random.randint(0, 30000),
        )
        if future:
            date = today + delta
        else:
            date = today - delta
        str_date = date.strftime("%d.%m.%Y")
        verb = self.command_instance.raw_command.lower().replace("когда", "").replace("ё", "е").lstrip()
        if verb == "":
            super()._return_answer(f"{rest_text} в {str_date}")
        return super()._return_answer(f"{rest_text} {verb} в {str_date}")

    @staticmethod
    def _show_all_commands() -> str:
        result = ""
        for command in CommandSettings().command_settings:
            result += f"{'Команды' if len(command.aliases) > 1 else 'Команда'}: [{', '.join(command.aliases[:3])}]"
            if command.description is not None:
                result += f" - {command.description}\n"
            else:
                result += "\n"
        return result

    async def _get_values_for_replacing(self):
        entities = await self.db.execute(
            select(AnswerEntity.key, AnswerEntity.value).where(
                and_(
                    AnswerEntity.pack_id == self.default_answer_pack.id,
                    AnswerEntity.content_type == AnswerEntityContentTypesEnum.TEXT,
                )
            )
        )
        keys = set()
        for key, value in entities.all():
            key_list, value_list = key.split(), value.split()
            keys.update(key_list)
            keys.update(value_list)
        return keys

    async def _replace_strategy(self, reply: BaseMessageSchema, content_type: AnswerEntityContentTypesEnum):
        values_for_replacing = await self._get_values_for_replacing()
        match content_type:
            case AnswerEntityContentTypesEnum.TEXT:
                words = reply.text.split()
                words_count = len(words)
                if words_count == 1:
                    coefficient = 1
                elif words_count == 2:
                    coefficient = 0.5
                else:
                    coefficient = 0.25
                for i in range(0, math.ceil(words_count * coefficient)):
                    words[random.randint(0, words_count - 1)] = random.choice(list(values_for_replacing))
                return " ".join(words)
            case _:
                raise NextStepException

    async def regenerate_message(self):
        self._check_reply_existed()
        if not self.default_answer_pack:
            self.default_answer_pack: AnswerPack = await AnswerPack.create_by_chat_id(
                self.db, self.member_service.chat.id
            )
        reply = self.message_service.message.reply
        value, content_type, description = self._select_content_from_reply(reply)
        result = await self._replace_strategy(reply, content_type)
        return super()._return_answer(result)

    def help(self):
        result = f"Привет, меня зовут {BOT_NAME}.\nМожете называть меня {ALTER_NAMES}\n\n"

        if not self.command_instance.rest_text:
            result += self._show_all_commands()
            return super()._return_answer(result)

        command = CommandSettings().alias_to_settings.get(self.command_instance.rest_text)
        if not command:
            return super()._return_answer(self._show_all_commands())

        result += f"{'Команды' if len(command.aliases) > 1 else 'Команда'}: [{', '.join(command.aliases)}]\n"
        if command.description:
            result += f"   Описание: {command.description}\n"
        if command.available_parameters:
            result += f"   Параметры: {', '.join(command.available_parameters)}\n"
        if command.to_find_for_values:
            result += "   - Можно указать значение или ключ\n"
        if command.to_find_for_key_values:
            result += "   - Можно указать ключ и значение в виде: my_key=my_value\n"
        if command.to_find_for_values_list:
            result += "   - Можно указать список значений, перечисляя через ',' / 'или'\n"
        for i, example in enumerate(command.examples, 1):
            result += f"   Пример {i}: {example}\n"

        return super()._return_answer(result)
