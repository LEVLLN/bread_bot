import datetime
import random

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.services.commands.command_settings import CommandSettings
from bread_bot.common.services.handlers.command_methods.base_command_method import BaseCommandMethod
from bread_bot.common.utils.structs import EntertainmentCommandsEnum


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
            verb = "будет"
        return super()._return_answer(f"{rest_text} {verb} в {str_date}")

    @staticmethod
    def _show_all_commands() -> str:
        result = ""
        for command in CommandSettings().command_settings:
            result += f"{'Команды' if len(command.aliases) > 1 else 'Команда'}: [{', '.join(command.aliases)}]"
            if command.description is not None:
                result += f" - {command.description}\n"
            else:
                result += "\n"
        return result

    def help(self):
        if not self.command_instance.rest_text:
            return super()._return_answer(self._show_all_commands())

        result = ""
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
