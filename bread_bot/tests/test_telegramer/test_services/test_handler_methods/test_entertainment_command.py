import pytest

from bread_bot.telegramer.schemas.commands import (
    ValueListCommandSchema, CommandSchema,
)
from bread_bot.telegramer.services.handlers.command_methods.entertainment_command_method import \
    EntertainmentCommandMethod
from bread_bot.telegramer.utils.structs import EntertainmentCommandsEnum


class TestEntertainmentCommand:
    @pytest.fixture
    async def entertainment_command_method(
            self,
            db,
            message_service,
            member_service,
            command_instance,
    ):
        yield EntertainmentCommandMethod(
            db=db,
            member_service=member_service,
            message_service=message_service,
            command_instance=command_instance,
        )

    @pytest.fixture
    async def command_instance(self, ):
        yield CommandSchema(
            header="хлеб",
            command=EntertainmentCommandsEnum.CHANCE,
            rest_text="события",
            raw_command="вероятность"
        )

    async def test_chance(self, entertainment_command_method):
        result = await entertainment_command_method.execute()
        assert result.text.startswith("Есть вероятность события - ")

    @pytest.mark.parametrize(
        "value_list",
        [
            ["1", "2", "3", "4"],
            ["1"],
            ["4", "6"],
        ]
    )
    async def test_choose_variant(self, entertainment_command_method, value_list):
        command_instance = ValueListCommandSchema(
            header="хлеб",
            command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
            rest_text="события",
            raw_command="шанс",
            value_list=value_list
        )
        entertainment_command_method.command_instance = command_instance

        result = await entertainment_command_method.execute()

        assert result.text in value_list

    async def test_random(self, entertainment_command_method, command_instance):
        command_instance.command = EntertainmentCommandsEnum.RANDOM
        entertainment_command_method.command_instance = command_instance

        result = await entertainment_command_method.execute()

        assert result.text.isnumeric()

    async def test_help_without_rest_text(self, entertainment_command_method, command_instance):
        command_instance.rest_text = ""
        command_instance.command = EntertainmentCommandsEnum.HELP
        command_instance.raw_command = "help"

        result = await entertainment_command_method.execute()

        assert "Команда: [покажи] - Показывает сохраненные данные\n" in result.text
        assert "Команды: [кто, у кого, кем, с кем, кого, кому, о ком, чья, чьё, чей, чье]" \
               " - Выбор случайного участника группы\n" in result.text

    @pytest.mark.parametrize(
        "rest_text, expected_result",
        [
            (
                    "покажи",
                    "Команда: [покажи]\n"
                    "   Описание: Показывает сохраненные данные\n"
                    "   Параметры: подстроку, подстроки, триггер, триггеры\n"
                    "   Пример 1: Хлеб покажи подстроки\n"
                    "   Пример 2: Хлеб покажи триггеры\n"
            ),
            (
                    "добавь",
                    "Команда: [добавь]\n"
                    "   Описание: Добавление указанных данных\n"
                    "   Параметры: подстроку, подстроки, триггер, триггеры\n"
                    "   - Можно указать ключ и значение в виде: my_key=my_value\n"
                    "   Пример 1: Хлеб добавь подстроку my_key=my_value\n"
                    "   Пример 2: Хлеб добавь триггер my_key=my_value\n"
            ),
            (
                    "удали",
                    "Команда: [удали]\n"
                    "   Описание: Удаляет указанные данные\n"
                    "   Параметры: подстроку, подстроки, триггер, триггеры\n"
                    "   - Можно указать значение или ключ\n"
                    "   - Можно указать ключ и значение в виде: my_key=my_value\n"
                    "   Пример 1: Хлеб удали подстроки my_key\n"
                    "   Пример 2: Хлеб удали триггер my_key\n"
                    "   Пример 3: Хлеб удали подстроки my_key=my_value\n"
            ),
            (
                    "процент",
                    "Команды: [процент срабатывания, процент]\n"
                    "   Описание: Показ / Установка процента срабатывания подстрок\n"
                    "   - Можно указать значение или ключ\n"
                    "   Пример 1: Хлеб процент\n"
                    "   Пример 2: Хлеб процент 15\n"
            ),
            (
                    "выбери",
                    "Команды: [выбери, выбор]\n"
                    "   Описание: Выбор случайного значения из перечисленных\n"
                    "   - Можно указать список значений, перечисляя через ',' / 'или'\n"
                    "   Пример 1: Хлеб выбери 1, 2, 3, 4\n"
                    "   Пример 2: Хлеб выбери 1 или 2 или 3 или 4\n"
            ),
        ]
    )
    async def test_help_with_rest_text(
            self,
            entertainment_command_method,
            command_instance,
            rest_text,
            expected_result,
    ):
        command_instance.rest_text = rest_text
        command_instance.command = EntertainmentCommandsEnum.HELP
        command_instance.raw_command = "help"

        result = await entertainment_command_method.execute()

        assert result.text == expected_result
