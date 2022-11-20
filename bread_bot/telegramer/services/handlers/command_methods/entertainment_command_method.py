import random

from bread_bot.telegramer.exceptions.base import NextStepException
from bread_bot.telegramer.services.commands.command_settings import CommandSettings
from bread_bot.telegramer.services.handlers.command_methods.base_command_method import BaseCommandMethod
from bread_bot.telegramer.utils.structs import EntertainmentCommandsEnum


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
            case _:
                raise NextStepException("Не найдена команде")

    def get_chance(self):
        return super()._return_answer(
            f"Есть вероятность {self.command_instance.rest_text} - "
            f"{str(random.randint(0, 100))}%")

    def choose_variant(self):
        return super()._return_answer(random.choice(self.command_instance.value_list).strip())

    def get_random(self):
        return super()._return_answer(str(random.randint(0, 10000)))

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
            result += f"   - Можно указать значение или ключ\n"
        if command.to_find_for_key_values:
            result += f"   - Можно указать ключ и значение в виде: my_key=my_value\n"
        if command.to_find_for_values_list:
            result += f"   - Можно указать список значений, перечисляя через ',' / 'или'\n"
        for i, example in enumerate(command.examples, 1):
            result += f"   Пример {i}: {example}\n"

        return super()._return_answer(result)
