import pytest

from bread_bot.telegramer.exceptions.commands import (
    NotAvailableCommandException,
    CommandParseException,
)
from bread_bot.telegramer.schemas.commands import (
    ParameterCommandSchema,
    ValueListCommandSchema,
    KeyValueParameterCommandSchema,
    ValueParameterCommandSchema,
    CommandSchema,
    ValueCommandSchema,
    ValueListParameterCommandSchema,
)
from bread_bot.telegramer.services.commands.command_parser import CommandParser
from bread_bot.telegramer.utils.structs import (
    AdminCommandsEnum,
    EntertainmentCommandsEnum,
    CommandAnswerParametersEnum,
    CommandKeyValueParametersEnum,
)


class TestCommandParser:
    @pytest.mark.parametrize(
        "message_text, expected_result",
        [
            ("Хлеб,совет", ("Хлеб", "совет")),
            ("Хлеб, совет как дела, дорогой?", ("Хлеб", "совет как дела, дорогой?")),
            ("Хлеб,  совет", ("Хлеб", "совет")),
            ("Хлеб совет", ("Хлеб", "совет")),
            ("Хлеб  совет", ("Хлеб", "совет")),
            ("Хлеб совет как дела дорогой?", ("Хлеб", "совет как дела дорогой?")),
            ("хлеб совет как дела дорогой?", ("хлеб", "совет как дела дорогой?")),
        ],
        ids=[
            "comma",
            "comma and space and rest text",
            "comma and 2 space",
            "space",
            "2 space",
            "space and rest text",
            "lower_case space and rest text",
        ]
    )
    async def test_parse_header(self, message_text, expected_result):
        command_parser: CommandParser = CommandParser(message_text)
        assert command_parser._find_header() == expected_result

    @pytest.mark.parametrize(
        "message_text, expected_result",
        [
            (
                    "Хлеб покажи подстроки как дела дорогой?",
                    ParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.SHOW,
                        parameter=CommandAnswerParametersEnum.SUBSTRING_LIST,
                        rest_text="как дела дорогой?"
                    )
            ),
            (
                    "Хлеб покажи подстроки",
                    ParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.SHOW,
                        parameter=CommandAnswerParametersEnum.SUBSTRING_LIST,
                        rest_text=""
                    )
            ),
            (
                    "Хлеб выбери 1, 2, 3, 4",
                    ValueListCommandSchema(
                        header="Хлеб",
                        command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
                        value_list=["1", "2", "3", "4"],
                        rest_text=""
                    )
            ),
            (
                    "Хлеб выбери 1 или 2 или 3 или 4",
                    ValueListCommandSchema(
                        header="Хлеб",
                        command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
                        value_list=["1", "2", "3", "4"],
                        rest_text=""
                    )
            ),
            (
                    "Хлеб выбери 1",
                    ValueListCommandSchema(
                        header="Хлеб",
                        command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
                        value_list=["1"],
                        rest_text=""
                    )
            ),
            (
                    "Хлеб добавь подстроку my_key=my_value",
                    KeyValueParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.ADD,
                        parameter=CommandAnswerParametersEnum.SUBSTRING,
                        key="my_key",
                        value="my_value"
                    )
            ),
            (
                    "Хлеб удали триггер my_value",
                    ValueParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.DELETE,
                        parameter=CommandAnswerParametersEnum.TRIGGER,
                        value="my_value"
                    )
            ),
            (
                    "Хлеб удали триггер my_key=my_value",
                    KeyValueParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.DELETE,
                        parameter=CommandAnswerParametersEnum.TRIGGER,
                        key="my_key",
                        value="my_value"
                    )
            ),
            (
                    "Хлеб процент срабатывания",
                    ValueCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.ANSWER_CHANCE,
                        rest_text="",
                        value="",
                    )
            ),
            (
                    "Хлеб процент срабатывания 20",
                    ValueCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.ANSWER_CHANCE,
                        rest_text="",
                        value="20",
                    )
            ),
            (
                    "Хлеб запомни значение my_key",
                    ValueListParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.REMEMBER,
                        parameter=CommandKeyValueParametersEnum.VALUE,
                        rest_text="",
                        value_list=["my_key"],
                    )
            ),
            (
                    "Хлеб запомни ключ my_value",
                    ValueListParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.REMEMBER,
                        parameter=CommandKeyValueParametersEnum.KEY,
                        rest_text="",
                        value_list=["my_value"],
                    )
            ),
            (
                    "Хлеб запомни ключи my_value1, my_value2",
                    ValueListParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.REMEMBER,
                        parameter=CommandKeyValueParametersEnum.KEY_LIST,
                        rest_text="",
                        value_list=["my_value1", "my_value2"],
                    )
            ),
            (
                    "Хлеб запомни значения my_key1, my_key2",
                    ValueListParameterCommandSchema(
                        header="Хлеб",
                        command=AdminCommandsEnum.REMEMBER,
                        parameter=CommandKeyValueParametersEnum.VALUE_LIST,
                        rest_text="",
                        value_list=["my_key1", "my_key2"],
                    )
            ),
            (
                    "Хлеб цитата",
                    CommandSchema(
                        header="Хлеб",
                        command=EntertainmentCommandsEnum.GQUOTE,
                        rest_text="",
                    )
            ),
            (
                    "Хлеб цитата значение test=test",
                    CommandSchema(
                        header="Хлеб",
                        command=EntertainmentCommandsEnum.GQUOTE,
                        rest_text="значение test=test",
                    )
            ),
        ]
    )
    async def test_parse_command(self, message_text, expected_result):
        command_parser: CommandParser = CommandParser(message_text)
        result = command_parser.parse()
        assert result == expected_result

    @pytest.mark.parametrize(
        "message_text, excepted_exception, expected_message",
        [
            ("Не хлеб, привет test test", NotAvailableCommandException, "Не найдено ключевое слово бота"),
            ("Хлеб", NotAvailableCommandException, "Не найдена команда"),
            ("Test Test Test", NotAvailableCommandException, "Не найдено ключевое слово бота"),
            ("Хлеб несуществующая_команда test", NotAvailableCommandException, "Не найдена команда"),
            ("Хлеб добавь", CommandParseException, "Не найдены параметры команды"),
            ("Хлеб покажи", CommandParseException, "Не найдены параметры команды"),
            ("Хлеб добавь подстроку", CommandParseException, "Не найдено ключ-значения"),
            ("Хлеб добавь подстроку my_value", CommandParseException, "Не найдено ключ-значения"),
            ("Хлеб запомни значение", CommandParseException, "Не найдено значения"),
        ]
    )
    async def test_parse_command_not_found(self, message_text, excepted_exception, expected_message):
        command_parser: CommandParser = CommandParser(message_text=message_text)
        with pytest.raises(excepted_exception) as e_info:
            command_parser.parse()
        assert e_info.value.args[0] == expected_message
