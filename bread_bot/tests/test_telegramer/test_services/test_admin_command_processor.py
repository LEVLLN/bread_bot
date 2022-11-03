import pytest
from sqlalchemy import and_

from bread_bot.telegramer.models import LocalMeme, Stats, Chat
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.services.message_service import MessageService
from bread_bot.telegramer.services.processors import AdminMessageProcessor
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum


class TestAdminMessageProcessor:
    @pytest.fixture
    async def processor(self, message_service) -> AdminMessageProcessor:
        processor = AdminMessageProcessor(message_service=message_service)
        return processor

    @pytest.fixture
    async def voice_processor(self, db, reply_voice) -> AdminMessageProcessor:
        message_service = MessageService(db=db, request_body=reply_voice)
        await message_service.init()
        processor = AdminMessageProcessor(message_service=message_service)
        return processor

    @pytest.mark.parametrize(
        "command_params, expected_data, expected_memes_type",
        [
            (
                    "триггер key=value",
                    {"key": ["value"]},
                    LocalMemeTypesEnum.FREE_WORDS,
            ),
            (
                    "подстроку key=value",
                    {"key": ["value"]},
                    LocalMemeTypesEnum.SUBSTRING_WORDS,
            ),
            (
                    "оскорбление some_rude_word",
                    ["some_rude_word"],
                    LocalMemeTypesEnum.RUDE_WORDS,
            ),
            (
                    "триггер key1=value",
                    {"key1": ["value"]},
                    LocalMemeTypesEnum.FREE_WORDS,

            ),
            (
                    "триггер key1=value1",
                    {"key1": ["value1"]},
                    LocalMemeTypesEnum.FREE_WORDS,
            ),
            (
                    "триггер key1",
                    ["key1"],
                    LocalMemeTypesEnum.FREE_WORDS,
            ),
        ]
    )
    async def test_add_local_meme_creating(self, db, processor, command_params, expected_data, expected_memes_type):
        processor.message.text = f"хлеб добавь {command_params}"

        result = await processor.process()
        assert isinstance(result, TextAnswerSchema)
        assert result.text == f"Ура! У чата появились {expected_memes_type.value}"

        local_meme = await LocalMeme.async_first(
            db=db,
            where=and_(
                LocalMeme.chat_id == processor.chat.chat_id,
                LocalMeme.type == expected_memes_type.name,
            )
        )
        assert local_meme is not None
        assert local_meme.data == expected_data
        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.ADD_CONTENT.name)) is not None

    @pytest.mark.parametrize(
        "command_params, expected_answer",
        [
            (
                    "триггер ke=value",
                    "Ключ не может быть меньше 3х символов"
            ),
            (
                    "триггер k=value",
                    "Ключ не может быть меньше 3х символов"
            )
        ]
    )
    async def test_add_local_meme_creating_validation(self, db, processor, command_params, expected_answer):
        processor.message.text = f"хлеб добавь {command_params}"

        result = await processor.process()
        assert isinstance(result, TextAnswerSchema)
        assert result.text == expected_answer

        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.VALIDATION_ERROR.name)) is not None

    @pytest.mark.parametrize(
        "command_params, source_data, expected_data",
        [
            (
                    "триггер key=value",
                    {"key": ["value"]},
                    {"key": ["value"]},
            ),
            (
                    "триггер key1=value",
                    {"key": ["value"]},
                    {"key": ["value"], "key1": ["value"]}
            ),
            (
                    "триггер key=another_value",
                    {"key": ["value"]},
                    {"key": ["value", "another_value"]}
            ),
            (
                    "триггер key=another_value",
                    {"key": ["value"]},
                    {"key": ["value", "another_value"]}
            ),
            (
                    "триггер key=value",
                    {"key": []},
                    {"key": ["value"]}
            ),
            (
                    "триггер key=value",
                    ["value"],
                    ["value"]
            ),
            (
                    "триггер some_string",
                    ["value"],
                    ["value", "some_string"]
            ),
            (
                    "триггер some_string",
                    [],
                    ["some_string"]
            ),
        ]
    )
    async def test_update_local_meme(self, db, local_meme_factory, processor,
                                     command_params, expected_data, source_data):
        local_meme = await local_meme_factory(type=LocalMemeTypesEnum.FREE_WORDS.name, data=source_data,
                                              chat=processor.chat, data_voice=None, )
        assert local_meme.data == source_data
        processor.message.text = f"хлеб добавь {command_params}"

        result = await processor.process()
        assert isinstance(result, TextAnswerSchema)
        assert result.text in processor.COMPLETE_MESSAGES

        local_meme = await LocalMeme.async_first(
            db=db,
            where=and_(
                LocalMeme.chat_id == processor.chat.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.FREE_WORDS.name,
            )
        )
        assert local_meme is not None
        assert local_meme.data == expected_data
        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.ADD_CONTENT.name)) is not None

    @pytest.mark.parametrize(
        "command_params, source_data, expected_data, answer_is_complete",
        [
            (
                    "триггер key",
                    {"key": ["value"]},
                    {},
                    True
            ),
            (
                    "триггер key1",
                    {"key": ["value"], "key1": ["value"]},
                    {"key": ["value"]},
                    True
            ),
            (
                    "триггер key1",
                    {"key": ["value"]},
                    {"key": ["value"]},
                    False
            ),
            (
                    "триггер key=value",
                    {"key": ["value"]},
                    {"key": []},
                    True
            ),
            (
                    "триггер key=value2",
                    {"key": ["value1", "value2", "value3"]},
                    {"key": ["value1", "value3"]},
                    True
            ),
            (
                    "триггер key=value2",
                    {"key": ["value1"]},
                    {"key": ["value1"]},
                    True
            ),
            (
                    "триггер key=",
                    {"key": ["value1"]},
                    {"key": ["value1"]},
                    True
            ),
            (
                    "триггер some_string",
                    ["value1"],
                    ["value1"],
                    True
            ),
            (
                    "триггер some_string",
                    ["some_string"],
                    [],
                    True
            ),
            (
                    "триггер some_string",
                    [],
                    [],
                    True
            ),
        ]
    )
    async def test_delete_local_meme(self, db, processor, local_meme_factory,
                                     command_params, expected_data, source_data, answer_is_complete):
        local_meme = await local_meme_factory(type=LocalMemeTypesEnum.FREE_WORDS.name, data=source_data,
                                              chat=processor.chat, data_voice=None)
        assert local_meme.data == source_data
        processor.message.text = f"хлеб удали {command_params}"

        result = await processor.process()
        assert isinstance(result, TextAnswerSchema)
        assert (result.text in processor.COMPLETE_MESSAGES) is answer_is_complete

        local_meme = await LocalMeme.async_first(
            db=db,
            where=and_(
                LocalMeme.chat_id == processor.chat.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.FREE_WORDS.name,
            )
        )
        assert local_meme is not None
        assert local_meme.data == expected_data
        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.DELETE_CONTENT.name)) is not None

    @pytest.mark.parametrize(
        "reply_text, text, expected_data",
        [
            ("key", "хлеб запомни как ключ value", {"key": ["value"]}),
            ("outer_value", "хлеб запомни как значение my_key", {"my_key": ["outer_value"]}),
            ("key", "хлеб запомни ключ value", {"key": ["value"]}),
            ("outer_value", "хлеб запомни значение my_key", {"my_key": ["outer_value"]}),
        ]
    )
    async def test_remember_local_meme(self, db, processor, reply_text, text, expected_data):
        reply_message = processor.message.copy(deep=True)
        reply_message.text = reply_text
        processor.message.text = text
        processor.message.reply = reply_message

        await processor.process()

        local_meme = await LocalMeme.async_first(
            db=db,
            where=and_(
                LocalMeme.chat_id == processor.chat.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            )
        )
        assert local_meme.data == expected_data
        assert await Stats.async_first(db=db, where=and_(
            Stats.member_id == processor.member.id,
            Stats.chat_id == processor.chat.chat_id,
            Stats.slug == StatsEnum.ADD_CONTENT.name)) is not None

    @pytest.mark.parametrize(
        "file_id, text, expected_data",
        [
            ("key", "хлеб запомни как ключ value", None),
            ("outer_value", "хлеб запомни как значение my_key", {"my_key": ["outer_value"]}),
            ("key", "хлеб запомни ключ value", None),
            ("outer_value", "хлеб запомни значение my_key", {"my_key": ["outer_value"]}),
            ("existed_value", "хлеб запомни значение existed_key", {"existed_key": ["existed_value"]}),
        ]
    )
    @pytest.mark.parametrize(
        "is_existed_local_meme",
        [True, False]
    )
    async def test_remember_local_meme_voice(self, db, processor, file_id, reply_voice,
                                             text, expected_data, local_meme_factory, is_existed_local_meme):
        if is_existed_local_meme:
            await local_meme_factory(type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
                                     data={"existed_text_key": "kek"},
                                     chat=processor.chat, data_voice=None)
        processor.message = reply_voice.message
        processor.message.reply.voice.file_id = file_id
        processor.message.text = text

        await processor.process()

        local_meme = await LocalMeme.async_first(
            db=db,
            where=and_(
                LocalMeme.chat_id == processor.chat.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            )
        )
        if local_meme:
            assert local_meme.data_voice == expected_data
            assert await Stats.async_first(db=db, where=and_(
                Stats.member_id == processor.member.id,
                Stats.chat_id == processor.chat.chat_id,
                Stats.slug == StatsEnum.ADD_CONTENT.name)) is not None

    @pytest.mark.parametrize(
        "file_id, text, expected_data",
        [
            ("key", "хлеб запомни как ключ value", None),
            ("outer_value", "хлеб запомни как значение my_key", {"my_key": ["outer_value"]}),
            ("key", "хлеб запомни ключ value", None),
            ("outer_value", "хлеб запомни значение my_key", {"my_key": ["outer_value"]}),
            ("existed_value", "хлеб запомни значение existed_key", {"existed_key": ["existed_value"]}),
        ]
    )
    @pytest.mark.parametrize(
        "is_existed_local_meme",
        [True, False]
    )
    async def test_remember_local_meme_photo(self, db, processor, file_id, reply_photo,
                                             text, expected_data, local_meme_factory, is_existed_local_meme):
        if is_existed_local_meme:
            await local_meme_factory(type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
                                     data={"existed_text_key": "kek"},
                                     chat=processor.chat, data_photo=None)
        processor.message = reply_photo.message
        processor.message.reply.photo[0].file_id = file_id
        processor.message.text = text

        await processor.process()

        local_meme = await LocalMeme.async_first(
            db=db,
            where=and_(
                LocalMeme.chat_id == processor.chat.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            )
        )
        if local_meme:
            assert local_meme.data_photo == expected_data
            assert await Stats.async_first(db=db, where=and_(
                Stats.member_id == processor.member.id,
                Stats.chat_id == processor.chat.chat_id,
                Stats.slug == StatsEnum.ADD_CONTENT.name)) is not None

    @pytest.mark.parametrize(
        "file_id, text, expected_data",
        [
            ("key", "хлеб запомни как ключ value", None),
            ("outer_value", "хлеб запомни как значение my_key", {"my_key": ["outer_value"]}),
            ("key", "хлеб запомни ключ value", None),
            ("outer_value", "хлеб запомни значение my_key", {"my_key": ["outer_value"]}),
            ("existed_value", "хлеб запомни значение existed_key", {"existed_key": ["existed_value"]}),
        ]
    )
    @pytest.mark.parametrize(
        "is_existed_local_meme",
        [True, False]
    )
    async def test_remember_local_meme_sticker(self, db, processor, file_id, reply_sticker,
                                               text, expected_data, local_meme_factory, is_existed_local_meme):
        if is_existed_local_meme:
            await local_meme_factory(type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
                                     data={"existed_text_key": "kek"},
                                     chat=processor.chat, data_sticker=None)
        processor.message = reply_sticker.message
        processor.message.reply.sticker.file_id = file_id
        processor.message.text = text

        await processor.process()

        local_meme = await LocalMeme.async_first(
            db=db,
            where=and_(
                LocalMeme.chat_id == processor.chat.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            )
        )
        if local_meme:
            assert local_meme.data_sticker == expected_data
            assert await Stats.async_first(db=db, where=and_(
                Stats.member_id == processor.member.id,
                Stats.chat_id == processor.chat.chat_id,
                Stats.slug == StatsEnum.ADD_CONTENT.name)) is not None

    @pytest.mark.parametrize(
        "text",
        [
            "хлеб запомни как ключ value",
            "хлеб запомни как значение my_key",
        ]
    )
    async def test_remember_local_meme_without_reply(self, db, processor, text):
        assert processor.message.reply is None
        processor.message.text = text

        result = await processor.process()

        assert result.text == "Выбери сообщение, которое запомнить"

    @pytest.mark.parametrize(
        "text, meme_type",
        [
            ("Хлеб покажи триггеры", LocalMemeTypesEnum.FREE_WORDS.name),
            ("Хлеб покажи подстроки", LocalMemeTypesEnum.SUBSTRING_WORDS.name),
            ("Хлеб покажи оскорбления", LocalMemeTypesEnum.RUDE_WORDS.name),
        ]
    )
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                    {"key": ["value", "value1"], "key2": ["value2"]},
                    "key = [value; value1]\nkey2 = [value2]"
            ),
            (
                    {"key": ["value"]},
                    "key = [value]"
            ),
            (
                    {},
                    "У группы отсутствуют"
            ),
            (
                    {"key": []},
                    "key = []"
            ),
            (
                    ["value1", "value2", "value3"],
                    "[value1; value2; value3]"
            ),
            (
                    [],
                    "У группы отсутствуют"
            )

        ]
    )
    async def test_show_local_memes(self, db, processor, local_meme_factory, text, meme_type, data, expected):
        processor.message.text = text
        await local_meme_factory(
            chat=processor.chat,
            data=data,
            type=meme_type,
            data_voice=None,
        )

        result = await processor.process()
        assert result.text == expected or result.text.startswith(expected)

    @pytest.mark.parametrize(
        "text, expected, is_completed_message, expected_text",
        [
            ("Хлеб процент срабатывания 100", 100, True, ""),
            ("Хлеб процент срабатывания 99", 99, True, ""),
            ("Хлеб процент срабатывания 0", 0, True, ""),
            ("Хлеб процент срабатывания", 100, False, "100"),
            ("Хлеб процент срабатывания 101", 100, False, "Некорректное значение. Необходимо ввести число от 0 до 100"),
            ("Хлеб процент срабатывания -1", 100, False, "Некорректное значение. Необходимо ввести число от 0 до 100"),
        ]
    )
    async def test_handle_answer_chance(self, db, processor, text, expected, is_completed_message, expected_text):
        processor.message.text = text

        result = await processor.process()
        chat = await Chat.async_first(db=db, where=Chat.id == processor.chat.id)

        assert chat.answer_chance == expected
        if is_completed_message:
            assert result.text in processor.COMPLETE_MESSAGES
        else:
            assert result.text == expected_text

    @pytest.mark.parametrize(
        "text, is_edited_trigger, expected, expected_text",
        [
            ("Хлеб редактирование", True, False, "Выключено реагирование на редактирование сообщений"),
            ("Хлеб редактирование", False, True, "Включено реагирование на редактирование сообщений")
        ]
    )
    async def test_set_edited_trigger(self, db, processor, text, is_edited_trigger, expected, expected_text):
        chat = processor.chat
        chat.is_edited_trigger = is_edited_trigger
        await Chat.async_add(db=db, instance=chat)
        processor.message.text = text
        processor.chat = chat

        result = await processor.process()

        chat = await Chat.async_first(db=db, where=Chat.id == processor.chat.id)
        assert chat.is_edited_trigger is expected
        assert result.text == expected_text

    @pytest.mark.parametrize(
        "text, is_voice_trigger, expected, expected_text",
        [
            ("Хлеб голосовые", True, False, "Выключено реагирование на голосовые сообщения"),
            ("Хлеб голосовые", False, True, "Включено реагирование на голосовые сообщения")
        ]
    )
    async def test_set_voice_trigger(self, db, processor, text, is_voice_trigger, expected, expected_text):
        chat = processor.chat
        chat.is_voice_trigger = is_voice_trigger
        await Chat.async_add(db=db, instance=chat)
        processor.message.text = text
        processor.chat = chat

        result = await processor.process()

        chat = await Chat.async_first(db=db, where=Chat.id == processor.chat.id)
        assert chat.is_voice_trigger is expected
        assert result.text == expected_text

    async def test_propagate_data(self, db, processor):
        processor.message.text = f"Хлеб распространи в {processor.chat.name}"

        result = await processor.process()

        assert result.text
