import pytest

from bread_bot.telegramer.services.processors import (
    MessageProcessor,
)


class TestMessageProcessor:
    @pytest.mark.parametrize(
        "text, trigger_word, command, params",
        [
            ("Some", "", "", ""),
            ("Хлеб привет", "Хлеб", "", "привет"),
            ("Хлеб топ тестов", "Хлеб", "топ", "тестов"),
            ("Хлеб топ тестов и другие слова", "Хлеб", "топ", "тестов и другие слова"),
            ("Хлеб добавь подстроку key=value", "Хлеб", "добавь", "подстроку key=value"),
        ],
    )
    async def test_parse_command(self, message_service, db, text, trigger_word, command, params):
        processor = MessageProcessor(message_service=message_service)
        processor.message.text = text
        await processor.parse_command(["топ", "добавь"])
        assert processor.trigger_word == trigger_word
        assert processor.command == command
        assert processor.command_params == params

    @pytest.mark.parametrize(
        "text, trigger_word, command, params, sub_command, key, value",
        [
            ("Some", "", "", "", None, None, None),
            ("Хлеб привет", "Хлеб", "", "привет", None, None, None),
            ("Хлеб топ тестов", "Хлеб", "топ", "тестов", None, None, None),
            ("Хлеб топ тестов и другие слова", "Хлеб", "топ", "тестов и другие слова", None, None, None),
            ("Хлеб добавь подстроку key=value", "Хлеб", "добавь", "подстроку key=value", "some_value1", "key", "value"),
            ("Хлеб добавь триггер key=value", "Хлеб", "добавь", "триггер key=value", "some_value2", "key", "value"),
        ],
    )
    async def test_parse_sub_command(self, message_service, db, text, trigger_word,
                                     command, params, sub_command, key, value):
        processor = MessageProcessor(message_service=message_service)
        processor.message.text = text
        await processor.parse_command(["топ", "добавь"])
        assert processor.trigger_word == trigger_word
        assert processor.command == command
        assert processor.command_params == params

        result = await processor.parse_sub_command({"подстроку": "some_value1", "триггер": "some_value2"})
        assert result == (sub_command, key, value)
