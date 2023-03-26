import pytest

from bread_bot.common.exceptions.commands import (
    CommandParseException,
    NotAvailableCommandException,
)
from bread_bot.common.schemas.commands import (
    CommandSchema,
    KeyValueParameterCommandSchema,
    ParameterCommandSchema,
    ValueCommandSchema,
    ValueListCommandSchema,
    ValueParameterCommandSchema,
)
from bread_bot.common.services.commands.command_parser import CommandParser
from bread_bot.common.utils.structs import (
    AdminCommandsEnum,
    CommandAnswerParametersEnum,
    EntertainmentCommandsEnum,
    IntegrationCommandsEnum,
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
        ],
    )
    async def test_parse_header(self, message_text, expected_result):
        command_parser: CommandParser = CommandParser(message_text)
        assert command_parser._find_header() == expected_result

    @pytest.mark.parametrize(
        "message_text, expected_result",
        [
            (
                "Хлеб когда был месяц май?",
                CommandSchema(
                    header="Хлеб",
                    command=EntertainmentCommandsEnum.PAST_DATE,
                    rest_text="месяц май?",
                    raw_command="когда был",
                ),
            ),
            (
                "Хлеб покажи подстроки как дела дорогой?",
                ParameterCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.SHOW,
                    parameter=CommandAnswerParametersEnum.SUBSTRING_LIST,
                    rest_text="как дела дорогой?",
                    raw_command="покажи",
                ),
            ),
            (
                "Хлеб покажи подстроки",
                ParameterCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.SHOW,
                    parameter=CommandAnswerParametersEnum.SUBSTRING_LIST,
                    rest_text="",
                    raw_command="покажи",
                ),
            ),
            (
                "Хлеб выбери 1, 2, 3, 4",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
                    value_list=["1", "2", "3", "4"],
                    rest_text="",
                    raw_command="выбери",
                ),
            ),
            (
                "Хлеб выбери 1 или 2 или 3 или 4",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
                    value_list=["1", "2", "3", "4"],
                    rest_text="",
                    raw_command="выбери",
                ),
            ),
            (
                "Хлеб выбери 1",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
                    value_list=["1"],
                    rest_text="",
                    raw_command="выбери",
                ),
            ),
            (
                "Хлеб добавь подстроку my_key=my_value",
                KeyValueParameterCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.ADD,
                    parameter=CommandAnswerParametersEnum.SUBSTRING,
                    key="my_key",
                    value="my_value",
                    raw_command="добавь",
                ),
            ),
            (
                "Хлеб удали триггер my_value",
                ValueParameterCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.DELETE,
                    parameter=CommandAnswerParametersEnum.TRIGGER,
                    value="my_value",
                    raw_command="удали",
                ),
            ),
            (
                "Хлеб удали триггер my_key=my_value",
                KeyValueParameterCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.DELETE,
                    parameter=CommandAnswerParametersEnum.TRIGGER,
                    key="my_key",
                    value="my_value",
                    raw_command="удали",
                ),
            ),
            (
                "Хлеб процент срабатывания",
                CommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.ANSWER_CHANCE,
                    rest_text="",
                    raw_command="процент срабатывания",
                ),
            ),
            (
                "Хлеб процент срабатывания 20",
                ValueCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.ANSWER_CHANCE,
                    rest_text="",
                    value="20",
                    raw_command="процент срабатывания",
                ),
            ),
            (
                "Хлеб скажи слово",
                ValueCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.SAY,
                    rest_text="",
                    value="слово",
                    raw_command="скажи",
                ),
            ),
            (
                "Хлеб проверка привет",
                ValueCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.CHECK_ANSWER,
                    rest_text="",
                    value="привет",
                    raw_command="проверка",
                ),
            ),
            (
                "Хлеб скажи",
                CommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.SAY,
                    rest_text="",
                    raw_command="скажи",
                ),
            ),
            (
                "Хлеб процент 20",
                ValueCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.ANSWER_CHANCE,
                    rest_text="",
                    value="20",
                    raw_command="процент",
                ),
            ),
            (
                "Хлеб запомни my_key",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.REMEMBER,
                    rest_text="",
                    value_list=["my_key"],
                    raw_command="запомни",
                ),
            ),
            (
                "Хлеб запомни значение my_key",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.REMEMBER,
                    rest_text="",
                    value_list=["my_key"],
                    raw_command="запомни значение",
                ),
            ),
            (
                "Хлеб запомни my_value",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.REMEMBER,
                    rest_text="",
                    value_list=["my_value"],
                    raw_command="запомни",
                ),
            ),
            (
                "Хлеб запомни my_value1, my_value2",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.REMEMBER,
                    rest_text="",
                    value_list=["my_value1", "my_value2"],
                    raw_command="запомни",
                ),
            ),
            (
                "Хлеб запомни my_key1, my_key2",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.REMEMBER,
                    rest_text="",
                    value_list=["my_key1", "my_key2"],
                    raw_command="запомни",
                ),
            ),
            (
                "Хлеб подстрока my_key1, my_key2",
                ValueListCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.REMEMBER,
                    rest_text="",
                    value_list=["my_key1", "my_key2"],
                    raw_command="подстрока",
                ),
            ),
            (
                "Хлеб цитата",
                CommandSchema(
                    header="Хлеб",
                    command=IntegrationCommandsEnum.QUOTE,
                    rest_text="",
                    raw_command="цитата",
                ),
            ),
            (
                "Хлеб цитата test=test",
                CommandSchema(
                    header="Хлеб",
                    command=IntegrationCommandsEnum.QUOTE,
                    rest_text="test=test",
                    raw_command="цитата",
                ),
            ),
            (
                "Хлеб цитата цит",
                CommandSchema(
                    header="Хлеб",
                    command=IntegrationCommandsEnum.QUOTE,
                    rest_text="цит",
                    raw_command="цитата",
                ),
            ),
            (
                "Хлеб удали подстроки лол, цит",
                ValueParameterCommandSchema(
                    header="Хлеб",
                    command=AdminCommandsEnum.DELETE,
                    rest_text="",
                    parameter=CommandAnswerParametersEnum.SUBSTRING_LIST,
                    raw_command="удали",
                    value="лол, цит",
                ),
            ),
        ],
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
            ("Хлеб запомни", CommandParseException, "Введены неправильные значения"),
        ],
    )
    async def test_parse_command_not_found(self, message_text, excepted_exception, expected_message):
        command_parser: CommandParser = CommandParser(message_text=message_text)
        with pytest.raises(excepted_exception) as e_info:
            command_parser.parse()
        assert e_info.value.args[0] == expected_message
