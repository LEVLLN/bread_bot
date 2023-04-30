import datetime

import pytest

from bread_bot.common.models import AnswerPacksToChats, AnswerPack, AnswerEntity
from bread_bot.common.schemas.commands import (
    ValueListCommandSchema,
    CommandSchema,
)
from bread_bot.common.services.handlers.command_methods.entertainment_command_method import EntertainmentCommandMethod
from bread_bot.common.services.messages.message_service import MessageService
from bread_bot.common.utils.structs import (
    EntertainmentCommandsEnum,
    AnswerEntityContentTypesEnum,
)


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
    async def command_instance(
        self,
    ):
        yield CommandSchema(
            header="хлеб", command=EntertainmentCommandsEnum.CHANCE, rest_text="события", raw_command="вероятность"
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
        ],
    )
    async def test_choose_variant(self, entertainment_command_method, value_list):
        command_instance = ValueListCommandSchema(
            header="хлеб",
            command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
            rest_text="события",
            raw_command="шанс",
            value_list=value_list,
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

        assert "1) покажи\n" in result.text
        assert "14) кто, у кого, кем\n" in result.text

    @pytest.mark.parametrize(
        "rest_text, expected_result",
        [
            (
                "покажи",
                (
                    "Команда: [покажи]\n"
                    "   Описание: Показывает сохраненные данные\n"
                    "   Параметры: подстроку, подстроки, триггер, триггеры\n"
                    "   Пример 1: Хлеб покажи подстроки\n"
                    "   Пример 2: Хлеб покажи триггеры\n"
                ),
            ),
            (
                "добавь",
                (
                    "Команда: [добавь]\n"
                    "   Описание: Добавление указанных данных\n"
                    "   Параметры: подстроку, подстроки, триггер, триггеры\n"
                    "   - Можно указать ключ и значение в виде: my_key=my_value\n"
                    "   Пример 1: Хлеб добавь подстроку my_key=my_value\n"
                    "   Пример 2: Хлеб добавь триггер my_key=my_value\n"
                ),
            ),
            (
                "удали",
                (
                    "Команда: [удали]\n"
                    "   Описание: [Надо выбрать сообщение в качестве ответа] Удаляет указанные данные\n"
                    "   Пример 1: Хлеб удали\n"
                ),
            ),
            (
                "процент",
                (
                    "Команды: [процент срабатывания, процент]\n"
                    "   Описание: Показ / Установка процента срабатывания подстрок\n"
                    "   - Можно указать значение или ключ\n"
                    "   Пример 1: Хлеб процент\n"
                    "   Пример 2: Хлеб процент 15\n"
                ),
            ),
            (
                "выбери",
                (
                    "Команды: [выбери, выбор]\n"
                    "   Описание: Выбор случайного значения из перечисленных\n"
                    "   - Можно указать список значений, перечисляя через ',' / 'или'\n"
                    "   Пример 1: Хлеб выбери 1, 2, 3, 4\n"
                    "   Пример 2: Хлеб выбери 1 или 2 или 3 или 4\n"
                ),
            ),
        ],
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

    @pytest.mark.parametrize(
        "command, raw_command, expected_result",
        [
            (EntertainmentCommandsEnum.PAST_DATE, "когда было", "Some event было в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда была", "Some event была в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда были", "Some event были в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда был", "Some event был в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда случилось", "Some event случилось в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда случилась", "Some event случилась в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда случился", "Some event случился в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда случились", "Some event случились в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда настало", "Some event настало в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда настала", "Some event настала в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда настал", "Some event настал в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда настали", "Some event настали в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда наступило", "Some event наступило в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда наступила", "Some event наступила в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда наступил", "Some event наступил в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда наступили", "Some event наступили в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда произошло", "Some event произошло в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда произошли", "Some event произошли в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда произошла", "Some event произошла в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда произошел", "Some event произошел в"),
            (EntertainmentCommandsEnum.PAST_DATE, "когда произошёл", "Some event произошел в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда", "Some event  в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда будет", "Some event будет в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда будут", "Some event будут в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда настанет", "Some event настанет в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда настанут", "Some event настанут в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда случатся", "Some event случатся в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда случится", "Some event случится в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда произойдет", "Some event произойдет в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда произойдёт", "Some event произойдет в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда произойдут", "Some event произойдут в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда наступят", "Some event наступят в"),
            (EntertainmentCommandsEnum.FUTURE_DATE, "когда наступит", "Some event наступит в"),
        ],
    )
    async def test_date_command(
        self, entertainment_command_method, command_instance, command, raw_command, expected_result
    ):
        today = datetime.datetime.today()
        command_instance.rest_text = "Some event?"
        command_instance.command = command
        command_instance.raw_command = raw_command

        result = await entertainment_command_method.execute()

        assert result.text.startswith(expected_result)
        date = result.text.lstrip(expected_result)
        if command == EntertainmentCommandsEnum.FUTURE_DATE:
            assert datetime.datetime.strptime(date, "%d.%m.%Y") > today
        else:
            assert datetime.datetime.strptime(date, "%d.%m.%Y") < today

    async def test_how_many(self, entertainment_command_method, command_instance):
        command_instance.rest_text = "Some event?"
        command_instance.command = EntertainmentCommandsEnum.HOW_MANY
        command_instance.raw_command = "сколько"

        result = await entertainment_command_method.execute()

        assert result.text.startswith("Some event - ")
        assert result.text.lstrip("Some event - ").isnumeric()


class TestRegenerateMessage:
    @pytest.fixture
    async def based_pack(self, db, member_service):
        answer_pack = await AnswerPack.async_add(db, instance=AnswerPack())
        await AnswerPacksToChats.async_add(
            db=db,
            instance=AnswerPacksToChats(
                chat_id=member_service.chat.id,
                pack_id=answer_pack.id,
            ),
        )
        yield answer_pack

    @pytest.fixture
    async def text_answer_entities(self, db, based_pack, member_service, command_method):
        for key in range(1, 10):
            await AnswerEntity.async_add(
                db=db,
                instance=AnswerEntity(
                    key="key" + str(key),
                    value="value" + str(key),
                    reaction_type="TRIGGER",
                    pack_id=based_pack.id,
                    content_type=AnswerEntityContentTypesEnum.TEXT,
                ),
            )
        yield None

    @pytest.fixture
    async def command_method(
        self,
        db,
        message_service,
        member_service,
        command_instance,
        based_pack,
    ):
        yield EntertainmentCommandMethod(
            db=db,
            member_service=member_service,
            message_service=message_service,
            command_instance=command_instance,
            default_answer_pack=based_pack,
        )

    @pytest.fixture
    async def photo_message_service(self, request_body_message, reply_photo) -> MessageService:
        message_service = MessageService(request_body=request_body_message)
        message_service.message.reply = reply_photo.message.reply
        yield message_service

    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield ValueListCommandSchema(
            header="хлеб",
            command=EntertainmentCommandsEnum.REGENERATE_MESSAGE,
            value_list=["my_value", "my_value1"],
            raw_command="запомни",
        )
