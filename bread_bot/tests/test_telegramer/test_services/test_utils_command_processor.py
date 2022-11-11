import pytest

from bread_bot.telegramer.clients.baneks_client import BaneksClient
from bread_bot.telegramer.clients.bashorg_client import BashOrgClient
from bread_bot.telegramer.schemas.api_models import ForismaticQuote, EvilInsultResponse, GreatAdviceResponse
from bread_bot.telegramer.schemas.bread_bot_answers import VoiceAnswerSchema
from bread_bot.telegramer.services.processors import UtilsCommandMessageProcessor
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, PropertiesEnum
from bread_bot.tests.resources.reader import bashorg_resource, baneks_resource


class TestUtilsCommandProcessor:
    @pytest.fixture
    async def processor(self, message_service, member_service) -> UtilsCommandMessageProcessor:
        processor = UtilsCommandMessageProcessor(message_service=message_service, member_service=member_service)
        return processor

    async def test_handle_rude_words(self, processor, local_meme_factory):
        await local_meme_factory(type=LocalMemeTypesEnum.RUDE_WORDS.name,
                                 data=["You are is bad"], chat=processor.chat, data_voice=None)
        reply_message = processor.message.copy(deep=True)
        processor.message.reply = reply_message
        processor.message.text = "Хлеб оскорби"

        result = await processor.process()
        assert result.text == "@Test_test\nYou are is bad"

    @pytest.mark.parametrize(
        "text",
        [
            "Хлеб выбери 1 или 2",
            "Хлеб выбери 1 или 2 или 3",
            "Хлеб выбери 1, 2",
            "Хлеб выбери 1, 2, 3",
        ]
    )
    async def test_choose_variant(self, processor, text):
        processor.message.text = text
        result = await processor.process()
        assert result.text in text

    @pytest.mark.parametrize(
        "text",
        [
            "Хлеб цит",
            "Хлеб цитата",
        ]
    )
    async def test_get_quote(self, processor, text, mocker):
        mock = mocker.patch(
            "bread_bot.telegramer.services.processors.utils_command_processor."
            "ForismaticClient.get_quote_text", return_value=ForismaticQuote(
                text='Some text',
                author='Some author'
            ))
        processor.message.text = text
        result = await processor.process()
        assert result.text == 'Some text\n\n© Some author'
        mock.assert_called_once()

    async def test_get_insult(self, processor, mocker):
        mock = mocker.patch(
            "bread_bot.telegramer.services.processors.utils_command_processor."
            "EvilInsultClient.get_evil_insult", return_value=EvilInsultResponse(
                insult='Some text',
                comment='Some author'
            ))
        processor.message.text = "Хлеб insult"
        result = await processor.process()
        assert result.text == 'Some text\n\n© Some author'
        mock.assert_called_once()
        # WITH REPLY
        processor.message.reply = processor.message
        result = await processor.process()
        assert result.text == '@Test_test\nSome text\n\n© Some author'

    async def test_get_joke_bashorg(self, processor, mocker):
        mocker.patch("random.choice", return_value=BashOrgClient)
        mock = mocker.patch(
            "bread_bot.telegramer.clients.bashorg_client."
            "BashOrgClient.get_quote", return_value=bashorg_resource)
        processor.message.text = "Хлеб анекдот"
        result = await processor.process()
        assert result.text == "xxx: Да я сто лет не бегал - я не смогу бежать со скоростью 5 миль в\n" \
                              "                час!\n" \
                              "yyy: Поверь, если за тобой будет гнаться спятивший робот Илона Маска - " \
                              "побежишь, как миленький.\n" \
                              "            \n\n© http://bashorg.org"
        mock.assert_called_once()

    async def test_get_joke_baneks(self, processor, mocker):
        mocker.patch("random.choice", return_value=BaneksClient)
        mock = mocker.patch(
            "bread_bot.telegramer.clients.baneks_client."
            "BaneksClient.get_quote", return_value=baneks_resource)
        processor.message.text = "Хлеб анекдот"
        result = await processor.process()
        assert result.text == "Купил мужик шляпу. Пришел домой, стал мерять, а она ему мала.\n\n© https://baneks.ru"
        mock.assert_called_once()

    async def test_get_num(self, processor, property_factory):
        property_object = await property_factory(
            slug=PropertiesEnum.DIGITS.name,
            data=["some_digits_data"],
        )
        processor.message.text = "Хлеб цифры"
        result = await processor.process()
        assert isinstance(result, VoiceAnswerSchema)
        assert result.voice == property_object.data[0]

    async def test_get_great_advice(self, processor, mocker):
        mock = mocker.patch(
            "bread_bot.telegramer.services.processors.utils_command_processor."
            "GreatAdviceClient.get_advice", return_value=GreatAdviceResponse(
                text='Some text',
                id=123,
            ))
        processor.message.text = "Хлеб совет"
        result = await processor.process()
        assert result.text == 'Some text'
        mock.assert_called_once()
