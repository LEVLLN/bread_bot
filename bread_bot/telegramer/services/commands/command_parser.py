import re
from typing import Tuple

from bread_bot.telegramer.exceptions.command_parser import (
    CommandNotFoundException,
    CommandParameterNotFoundException,
    HeaderNotFoundException,
    CommandKeyValueInvalidException,
)
from bread_bot.telegramer.schemas.commands import (
    CommandSchema,
    ParameterCommandSchema,
    ValueListCommandSchema,
    ValueCommandSchema,
    KeyValueParameterCommandSchema,
    ValueParameterCommandSchema,
    ValueListParameterCommandSchema,
    CommandSettingsSchema,
)
from bread_bot.telegramer.services.commands.command_settings import CommandSettings
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.functions import composite_mask
from bread_bot.telegramer.utils.structs import CommandAnswerParametersEnum, CommandKeyValueParametersEnum


class CommandParser:
    def __init__(self, message_text: str):
        self.message_text: str = message_text
        self.command_settings_service = CommandSettings()
        self.command_settings = None
        self.main_parameters: dict = {}

    @staticmethod
    def parse_properties(keys: list, source_text: str) -> Tuple[str, str]:
        """
        Парсинг свойств исходного текста и отделение ключевого значения
        """
        first_item, second_item = re.findall(
            f"^({composite_mask(keys)}).?\\s?(.+)?",
            source_text,
            re.IGNORECASE
        )[0]
        return first_item.strip(), second_item.strip()

    @staticmethod
    def split_rest(rest: str) -> list[str]:
        """
        Разделение сообщения на список значений
        """
        try:
            parameter_list = rest.split(" или ")
            if len(parameter_list) <= 1:
                parameter_list = rest.split(" и ")
            if len(parameter_list) <= 1:
                parameter_list = rest.split(",")
        except ValueError:
            parameter_list = [rest, ]
        return list(
            map(lambda x: x.strip(), parameter_list)
        )

    def _find_header(self) -> Tuple[str, str]:
        """
        Поиск обращения к боту
        """
        try:
            return self.parse_properties(structs.TRIGGER_WORDS, self.message_text)
        except IndexError:
            raise HeaderNotFoundException("Не найдено ключевое слово бота")

    def _find_command(self, rest: str) -> Tuple[str, str]:
        """
        Поиск команд
        """
        try:
            command, rest = self.parse_properties(self.command_settings_service.alias_list, rest)
        except IndexError:
            raise CommandNotFoundException("Не найдена команда")
        else:
            return command.strip().lower(), rest

    def _find_parameters(
            self,
            rest: str
    ) -> Tuple[CommandAnswerParametersEnum | CommandKeyValueParametersEnum, str]:
        """
        Поиск параметров
        """
        try:
            parameter, rest = self.parse_properties(self.command_settings.available_parameters, rest)
        except (IndexError, TypeError) as e:
            raise CommandParameterNotFoundException("Не найдены параметры команды")
        else:
            return self.command_settings_service.parameters_value_to_enum[parameter.strip().lower()], rest

    def _set_command_settings(self, command: str) -> None:
        """
        Установка настроек команды
        """
        try:
            self.command_settings = self.command_settings_service.alias_to_settings[command]
        except KeyError:
            raise CommandNotFoundException("Не найдена команда")
        else:
            self.main_parameters["command"] = self.command_settings.command

    def _handle_parameter_key_value(
            self,
            rest: str,
            to_raise_exception: bool,
    ) -> KeyValueParameterCommandSchema | ValueParameterCommandSchema:
        """
        Получение команды с параметром, значением или ключом и значением
        """
        parameter, rest = self._find_parameters(rest=rest)
        try:
            key, value = rest.split("=")
        except ValueError:
            if to_raise_exception:
                raise CommandKeyValueInvalidException("Не найдено ключ-значения")
            return ValueParameterCommandSchema(
                **self.main_parameters,
                parameter=parameter,
                value=rest,
            )
        else:
            return KeyValueParameterCommandSchema(
                **self.main_parameters,
                parameter=parameter,
                key=key,
                value=value,
            )

    def _handle_value_list(self, rest: str) -> ValueListCommandSchema:
        """
        Получение команды без параметра со списком значений
        """
        parameter_list = self.split_rest(rest=rest)
        return ValueListCommandSchema(
            **self.main_parameters,
            value_list=[parameter_list_item.strip() for parameter_list_item in parameter_list],
        )

    def _handle_parameter_value_list(self, rest: str) -> ValueListParameterCommandSchema:
        """
        Получение команды с параметром и списком значений
        """
        parameter, rest = self._find_parameters(rest=rest)
        if len(rest) == 0:
            raise CommandKeyValueInvalidException("Не найдено значения")
        parameter_list = self.split_rest(rest=rest)
        return ValueListParameterCommandSchema(
            **self.main_parameters,
            parameter=parameter,
            value_list=parameter_list,
        )

    def parse(self) -> CommandSchema:
        """
        Парсинг команды из строки в структуру
        """
        header, rest = self._find_header()
        self.main_parameters["header"] = header
        command, rest = self._find_command(rest=rest)
        self._set_command_settings(command=command)
        # Обработка команды
        match self.command_settings:
            # Команда + Параметр + Ключ + Значение | Параметр + Значение
            case CommandSettingsSchema(to_find_for_key_values=True, to_find_for_values=True):
                return self._handle_parameter_key_value(rest=rest, to_raise_exception=False)
            # Команда + Параметр + Значение
            case CommandSettingsSchema(to_find_for_key_values=True, available_parameters=_):
                return self._handle_parameter_key_value(rest=rest, to_raise_exception=True)
            # Команда + Список значений
            case CommandSettingsSchema(to_find_for_values_list=True):
                return self._handle_value_list(rest=rest)
            # Только Команда
            case CommandSettingsSchema(to_find_for_values=False, available_parameters=None):
                return CommandSchema(**self.main_parameters, rest_text=rest)
            # Команда + Значение
            case CommandSettingsSchema(to_find_for_values=True, available_parameters=None):
                return ValueCommandSchema(**self.main_parameters, value=rest)
            # Команда + Параметр + Список Значений + Без ключей
            case CommandSettingsSchema(to_find_for_key_values=False, available_parameters=_, to_find_for_values=True):
                return self._handle_parameter_value_list(rest=rest)
            # Команда + Параметр
            case CommandSettingsSchema(available_parameters=_):
                parameter, rest = self._find_parameters(rest=rest)
                return ParameterCommandSchema(**self.main_parameters, parameter=parameter, rest_text=rest)
            # Отсутствующие кейсы
            case _:
                raise CommandNotFoundException("Не определен тип команды")
