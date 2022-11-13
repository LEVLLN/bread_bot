import pytest

from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema, VoiceAnswerSchema, PhotoAnswerSchema, \
    StickerAnswerSchema
from bread_bot.telegramer.services.processors import PhrasesMessageProcessor
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum


class TestPhrasesMessageProcessor:
    @pytest.fixture
    async def processor(self, message_service, member_service) -> PhrasesMessageProcessor:
        processor = PhrasesMessageProcessor(message_service=message_service, member_service=member_service)
        return processor

    @pytest.fixture
    async def local_memes_trigger_collection(self, local_meme_factory, member_service):
        return await local_meme_factory(
            type=LocalMemeTypesEnum.FREE_WORDS.name,
            data={
                "some free word str": "value",
                "some_free_word": ["default answer"],
                "some free word 3": {"default answer": "value"},
                "some free word 2": ["default answer 2"],
                "key": ["trigger"]
            },
            data_voice=None,
            chat=member_service.chat
        )

    @pytest.fixture
    async def local_memes_substring_collection(self, local_meme_factory, member_service):
        return await local_meme_factory(
            type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            data={
                'my_substring': ['some_answer_in_list'],
                'my_str': 'some_answer_str',
                "ch": ["two_char_answer"],
                "key": ["substring"],
            },
            data_voice=None,
            chat=member_service.chat
        )

    @pytest.fixture
    async def local_memes_substring_voice_collection(self, local_meme_factory, member_service):
        return await local_meme_factory(
            type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            data=None,
            data_voice={
                'my_voice': ['some_answer_in_list_voice'],
                'my_voice_str': 'some_answer_str_voice',
                "ch": ["two_char_answer_voice"],
                "voice_key": ["substring_voice"],
            },
            chat=member_service.chat
        )

    @pytest.fixture
    async def local_memes_substring_photo_collection(self, local_meme_factory, member_service):
        return await local_meme_factory(
            type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            data=None,
            data_photo={
                'my_photo': ['some_answer_in_list_photo'],
                'my_photo_str': 'some_answer_str_photo',
                "ch": ["two_char_answer_photo"],
                "photo_key": ["substring_photo"],
            },
            chat=member_service.chat
        )

    @pytest.fixture
    async def local_memes_substring_sticker_collection(self, local_meme_factory, member_service):
        return await local_meme_factory(
            type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            data=None,
            data_sticker={
                'my_sticker': ['some_answer_in_list_sticker'],
                'my_sticker_str': 'some_answer_str_sticker',
                "ch": ["two_char_answer_sticker"],
                "sticker_key": ["substring_sticker"],
            },
            chat=member_service.chat
        )

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("Some free word", None),
            ("Some free word 2", "default answer 2"),
            ("Some_free_word", "default answer"),
            ("Some free word 1", None),
            ("Some free word 3", None),
            ("Some free word str", "value"),
            ("Хлеб Some free word str", "value"),
            ("Хлеб Some free word 3", None),
            ("Хлеб some_free_word", "default answer"),
        ]
    )
    async def test_handle_trigger_words(self, db, processor: PhrasesMessageProcessor,
                                        local_memes_trigger_collection, text, expected):
        processor.message.text = text
        result = await processor.get_trigger_words()
        expected_result = TextAnswerSchema(
            text=expected,
            reply_to_message_id=processor.message.message_id,
            chat_id=processor.chat.chat_id
        ) if expected else None
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("I triggered my_substring in message", "some_answer_in_list"),
            ("my_substring", "some_answer_in_list"),
            ("a my_substring b", "some_answer_in_list"),
            (".my_substring.", "some_answer_in_list"),
            ("my_str", "some_answer_str"),
            ("a my_str b", "some_answer_str"),
            ("I triggered ch in message", None),
            ("I triggered in message", None),
        ]
    )
    async def test_handle_substring_words(self, db, processor: PhrasesMessageProcessor,
                                          local_memes_substring_collection, text, expected):
        processor.message.text = text
        result = await processor.get_substring_words()
        expected_result = TextAnswerSchema(
            text=expected,
            reply_to_message_id=processor.message.message_id,
            chat_id=processor.chat.chat_id
        ) if expected else None
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("I triggered my_voice in message", "some_answer_in_list_voice"),
            ("my_voice", "some_answer_in_list_voice"),
            ("a my_voice b", "some_answer_in_list_voice"),
            (".my_voice.", "some_answer_in_list_voice"),
            ("my_voice_str", "some_answer_str_voice"),
            ("a my_voice_str b", "some_answer_str_voice"),
            ("I triggered ch in message", None),
            ("I triggered in message", None),
        ]
    )
    async def test_handle_substring_words_voice(self, db, processor: PhrasesMessageProcessor,
                                                local_memes_substring_voice_collection, text, expected):
        processor.message.text = text
        result = await processor.get_substring_words()
        expected_result = VoiceAnswerSchema(
            voice=expected,
            reply_to_message_id=processor.message.message_id,
            chat_id=processor.chat.chat_id
        ) if expected else None
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("I triggered my_photo in message", "some_answer_in_list_photo"),
            ("my_photo", "some_answer_in_list_photo"),
            ("a my_photo b", "some_answer_in_list_photo"),
            (".my_photo.", "some_answer_in_list_photo"),
            ("my_photo_str", "some_answer_str_photo"),
            ("a my_photo_str b", "some_answer_str_photo"),
            ("I triggered ch in message", None),
            ("I triggered in message", None),
        ]
    )
    async def test_handle_substring_words_photo(self, db, processor: PhrasesMessageProcessor,
                                                local_memes_substring_photo_collection, text, expected):
        processor.message.text = text
        result = await processor.get_substring_words()
        expected_result = PhotoAnswerSchema(
            photo=expected,
            reply_to_message_id=processor.message.message_id,
            chat_id=processor.chat.chat_id
        ) if expected else None
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("I triggered my_sticker in message", "some_answer_in_list_sticker"),
            ("my_sticker", "some_answer_in_list_sticker"),
            ("a my_sticker b", "some_answer_in_list_sticker"),
            (".my_sticker.", "some_answer_in_list_sticker"),
            ("my_sticker_str", "some_answer_str_sticker"),
            ("a my_sticker_str b", "some_answer_str_sticker"),
            ("I triggered ch in message", None),
            ("I triggered in message", None),
        ]
    )
    async def test_handle_substring_words_sticker(self, db, processor: PhrasesMessageProcessor,
                                                  local_memes_substring_sticker_collection, text, expected):
        processor.message.text = text
        result = await processor.get_substring_words()
        expected_result = StickerAnswerSchema(
            sticker=expected,
            reply_to_message_id=processor.message.message_id,
            chat_id=processor.chat.chat_id
        ) if expected else None
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("I triggered my_substring in message", "some_answer_in_list"),
            ("Some free word 2", "default answer 2"),
            ("key", "trigger"),
            ("some key", "substring")
        ]
    )
    async def test_process(self, db, processor: PhrasesMessageProcessor, local_memes_trigger_collection,
                           local_memes_substring_collection, text, expected):
        processor.message.text = text
        assert await processor.condition
        result = await processor.process()
        expected_result = TextAnswerSchema(
            text=expected,
            reply_to_message_id=processor.message.message_id,
            chat_id=processor.chat.chat_id
        ) if expected else None
        assert result == expected_result

    @pytest.mark.parametrize(
        "text, answer_chance, expected",
        [
            ("key", 100, "trigger"),
            ("key", 0, None),
        ]
    )
    async def test_chance(self, db, processor: PhrasesMessageProcessor,
                          local_memes_trigger_collection, text, expected, answer_chance):
        processor.message.text = text
        processor.chat.answer_chance = answer_chance

        result = await processor.process()
        expected_result = TextAnswerSchema(
            text=expected,
            reply_to_message_id=processor.message.message_id,
            chat_id=processor.chat.chat_id
        ) if expected else None
        assert result == expected_result
