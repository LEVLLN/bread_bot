import pytest

from bread_bot.common.clients.baneks_client import BaneksClient
from bread_bot.common.clients.evil_insult_client import EvilInsultClient
from bread_bot.common.clients.forismatic_client import ForismaticClient
from bread_bot.common.clients.great_advice import GreatAdviceClient
from bread_bot.common.exceptions.base import RaiseUpException
from bread_bot.common.schemas.api_models import GreatAdviceResponse, ForismaticQuote, EvilInsultResponse
from bread_bot.common.schemas.commands import (
    CommandSchema,
)
from bread_bot.common.services.handlers.command_methods.integration_command_method import IntegrationCommandMethod
from bread_bot.common.utils.structs import IntegrationCommandsEnum


class TestIntegrationCommand:
    @pytest.fixture
    async def integration_command_method(
        self,
        db,
        message_service,
        member_service,
        command_instance,
    ):
        yield IntegrationCommandMethod(
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
            header="хлеб", command=IntegrationCommandsEnum.ADVICE, rest_text="some test", raw_command="совет"
        )

    async def test_advice(self, mocker, integration_command_method):
        mock = mocker.patch.object(
            GreatAdviceClient,
            "get_advice",
            return_value=GreatAdviceResponse(
                text="Some text",
                id=123,
            ),
        )

        result = await integration_command_method.execute()

        assert result.text == "Some text"
        mock.assert_called_once()

    async def test_quote(self, mocker, integration_command_method):
        integration_command_method.command_instance.command = IntegrationCommandsEnum.QUOTE
        mock = mocker.patch.object(
            ForismaticClient,
            "get_quote_text",
            return_value=ForismaticQuote(
                text="Some text",
                author="some_author",
            ),
        )

        result = await integration_command_method.execute()

        assert result.text == "Some text\n\n© some_author"
        mock.assert_called_once()

    async def test_insult_without_reply(self, mocker, integration_command_method):
        integration_command_method.command_instance.command = IntegrationCommandsEnum.INSULT
        mock = mocker.patch.object(
            EvilInsultClient,
            "get_evil_insult",
            return_value=EvilInsultResponse(
                insult="Some insult",
                comment="some comment",
            ),
        )

        result = await integration_command_method.execute()

        assert result.text == "Some insult\n\n© some comment"
        mock.assert_called_once()

    async def test_insult_with_reply(self, mocker, integration_command_method, message_service):
        integration_command_method.message_service.message.reply = message_service.message
        integration_command_method.command_instance.command = IntegrationCommandsEnum.INSULT
        mock = mocker.patch.object(
            EvilInsultClient,
            "get_evil_insult",
            return_value=EvilInsultResponse(
                insult="Some insult",
                comment="some comment",
            ),
        )

        result = await integration_command_method.execute()

        assert result.text == f"@{message_service.message.source.username}\nSome insult\n\n© some comment"
        mock.assert_called_once()

    async def test_joke_error(self, mocker, integration_command_method):
        integration_command_method.command_instance.command = IntegrationCommandsEnum.JOKE
        mock = mocker.patch.object(BaneksClient, "get_text", return_value=None)

        with pytest.raises(RaiseUpException) as error:
            await integration_command_method.execute()
        assert error.value.args[0] == "Не получилось получить анекдот у поставщика"
        mock.assert_called_once()

    async def test_joke(self, mocker, integration_command_method):
        integration_command_method.command_instance.command = IntegrationCommandsEnum.JOKE
        mock = mocker.patch.object(BaneksClient, "get_text", return_value="some_joke")

        result = await integration_command_method.execute()

        assert result.text == f"some_joke\n\n© {BaneksClient().url}"
        mock.assert_called_once()
