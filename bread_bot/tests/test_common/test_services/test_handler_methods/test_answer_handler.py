import functools

import pytest

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.models import AnswerPack, AnswerPacksToChats, DictionaryEntity, AnswerEntity
from bread_bot.common.schemas.bread_bot_answers import (
    TextAnswerSchema,
    StickerAnswerSchema,
    VoiceAnswerSchema,
    PhotoAnswerSchema,
    GifAnswerSchema,
)
from bread_bot.common.services.handlers import answer_handler
from bread_bot.common.services.handlers.answer_handler import (
    SubstringAnswerHandler,
    TriggerAnswerHandler,
    PictureAnswerHandler,
    morphed_keys_cache,
)
from bread_bot.common.utils.structs import AnswerEntityReactionTypesEnum


class TestAnswerHandler:
    @pytest.fixture
    async def based_pack(self, db, member_service):
        answer_pack = await AnswerPack.get_by_chat_id(db, member_service.chat.id)
        if not answer_pack:
            answer_pack = await AnswerPack.async_add(db, instance=AnswerPack())
            await AnswerPacksToChats.async_add(
                db=db,
                instance=AnswerPacksToChats(
                    chat_id=member_service.chat.id,
                    pack_id=answer_pack.id,
                ),
            )
        answer_pack = await AnswerPack.get_by_chat_id(db, member_service.chat.id)
        yield answer_pack

    @pytest.fixture
    async def prepare_data(
        self,
        text_entity_factory,
        voice_entity_factory,
        photo_entity_factory,
        sticker_entity_factory,
        based_pack,
    ):
        for reaction_type in (AnswerEntityReactionTypesEnum.SUBSTRING, AnswerEntityReactionTypesEnum.TRIGGER):
            for key, value in [
                ("my_key", "my_value1"),
                ("my_key", "my_value2"),
                ("other_key", "my_value"),
            ]:
                await text_entity_factory(key=key, value=value, reaction_type=reaction_type, pack_id=based_pack.id)
                await voice_entity_factory(key=key, value=value, reaction_type=reaction_type, pack_id=based_pack.id)
                await sticker_entity_factory(key=key, value=value, reaction_type=reaction_type, pack_id=based_pack.id)
                await photo_entity_factory(key=key, value=value, reaction_type=reaction_type, pack_id=based_pack.id)

    @pytest.fixture
    async def picture_answer_handler(self, db, member_service, message_service, reply_photo):
        message_service.message = reply_photo.message.reply
        picture_answer_handler = PictureAnswerHandler(next_handler=None)
        picture_answer_handler.member_service = member_service
        picture_answer_handler.message_service = message_service
        picture_answer_handler.db = db
        picture_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(db, member_service.chat.id)
        yield picture_answer_handler

    @pytest.fixture
    async def substring_answer_handler(self, db, member_service, message_service, prepare_data):
        message_service.message.text = "My text consists of My_key and test test test"
        substring_answer_handler = SubstringAnswerHandler(next_handler=None)
        substring_answer_handler.member_service = member_service
        substring_answer_handler.message_service = message_service
        substring_answer_handler.db = db
        substring_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(db, member_service.chat.id)
        yield substring_answer_handler

    @pytest.fixture
    async def trigger_answer_handler(self, db, member_service, message_service, prepare_data):
        message_service.message.text = "my_key"
        trigger_answer_handler = TriggerAnswerHandler(next_handler=None)
        trigger_answer_handler.member_service = member_service
        trigger_answer_handler.message_service = message_service
        trigger_answer_handler.db = db
        trigger_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(db, member_service.chat.id)
        yield trigger_answer_handler

    async def test_process_substring(self, db, substring_answer_handler, prepare_data):
        result = await substring_answer_handler.process()
        assert type(result) in (
            TextAnswerSchema,
            PhotoAnswerSchema,
            VoiceAnswerSchema,
            StickerAnswerSchema,
            GifAnswerSchema,
        )

    async def test_process_concrete_substring(
        self,
        db,
        prepare_data,
        text_entity_factory,
        based_pack,
        substring_answer_handler,
    ):
        await text_entity_factory(
            key="concrete_key",
            value="my_concrete_value",
            pack_id=based_pack.id,
            reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING,
        )
        substring_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(
            db, substring_answer_handler.member_service.chat.id
        )
        substring_answer_handler.message_service.message.text = "I finding concrete_key in message"

        result = await substring_answer_handler.process()

        assert isinstance(result, TextAnswerSchema)
        assert result.text == "my_concrete_value"

    @pytest.mark.parametrize(
        "morph_text, entity_key, raw_word_in_text",
        [
            ("слова", "слово", "слову"),
            ("делать", "делаю", "делавший"),
            ("красивый", "красивая", "красивое"),
            ("зариф", "зарифу", "зарифа"),
            ("батарейка", "батарейка", "батарейка"),
            ("батарейка", "батарейка", "батарейки"),
            ("батарейка", "батарейки", "батарейка"),
            ("батарейки", "батарейка", "батарейка"),
            ("some_key", "some_key", "some_key"),
        ],
    )
    async def test_process_concrete_substring_in_morph(
        self,
        db,
        prepare_data,
        text_entity_factory,
        based_pack,
        substring_answer_handler,
        dictionary_entity_factory,
        morph_text,
        entity_key,
        raw_word_in_text,
    ):
        await dictionary_entity_factory(chat_id=substring_answer_handler.member_service.chat.id, value=morph_text)
        assert await DictionaryEntity.async_filter(
            db, DictionaryEntity.chat_id == substring_answer_handler.member_service.chat.id
        )
        await text_entity_factory(
            key=entity_key,
            value="concrete_value",
            pack_id=based_pack.id,
            reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING,
        )
        substring_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(
            db, substring_answer_handler.member_service.chat.id
        )
        substring_answer_handler.message_service.message.text = f"I finding {raw_word_in_text} in message"

        result = await substring_answer_handler.process()

        assert isinstance(result, TextAnswerSchema)
        assert result.text == "concrete_value"

    async def test_process_picture(self, db, prepare_data, picture_answer_handler, member_service, mocker):
        mocker.patch("bread_bot.common.services.handlers.answer_handler.random.random", return_value=0.15)
        result = await picture_answer_handler.process()
        assert result.text == f"Похоже на {member_service.member.first_name} {member_service.member.last_name}"

    async def test_process_concrete_gif_entity(
        self,
        db,
        substring_answer_handler,
        prepare_data,
        gif_entity_factory,
        based_pack,
    ):
        await gif_entity_factory(
            key="concrete_key",
            value="my_concrete_value",
            pack_id=based_pack.id,
            reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING,
        )
        substring_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(
            db, substring_answer_handler.member_service.chat.id
        )
        substring_answer_handler.message_service.message.text = "I finding concrete_key in message"

        result = await substring_answer_handler.process()

        assert isinstance(result, GifAnswerSchema)
        assert result.animation == "my_concrete_value"

    async def test_process_substring_without_keys(self, db, substring_answer_handler, prepare_data):
        substring_answer_handler.member_service.message.text = "Without keywords message"

        with pytest.raises(NextStepException) as error:
            await substring_answer_handler.process()
        assert error.value.args[0] == "Подходящих ключей не найдено"

    async def test_process_substring_without_entities(self, db, substring_answer_handler):
        substring_answer_handler.member_service.message.text = "Without keywords message"

        with pytest.raises(NextStepException) as error:
            await substring_answer_handler.process()
        assert error.value.args[0] == "Подходящих ключей не найдено"

    async def test_process_substring_not_pack(self, db, member_service, message_service):
        message_service.message.text = "My text consists of my_key and test test test"
        substring_answer_handler = SubstringAnswerHandler(next_handler=None)
        substring_answer_handler.member_service = member_service
        substring_answer_handler.message_service = message_service
        substring_answer_handler.db = db

        with pytest.raises(NextStepException) as error:
            await substring_answer_handler.process()
        assert error.value.args[0] == "Отсутствуют пакеты с ответами"

    async def test_process_trigger(self, db, trigger_answer_handler, prepare_data):
        result = await trigger_answer_handler.process()
        assert type(result) in (
            TextAnswerSchema,
            PhotoAnswerSchema,
            VoiceAnswerSchema,
            StickerAnswerSchema,
            GifAnswerSchema,
        )

    @pytest.mark.parametrize(
        "message_text",
        [
            "my_key bla bla",
            "bla bla bla",
            "test",
        ],
    )
    async def test_process_trigger_not_message(self, db, trigger_answer_handler, prepare_data, message_text):
        trigger_answer_handler.message_service.message.text = message_text

        with pytest.raises(NextStepException) as error:
            await trigger_answer_handler.process()
        assert error.value.args[0] == "Подходящих ключей не найдено"

    async def test_process_concrete_trigger(
        self,
        db,
        trigger_answer_handler,
        prepare_data,
        text_entity_factory,
        based_pack,
    ):
        await text_entity_factory(
            key="concrete_key",
            value="my_concrete_value",
            pack_id=based_pack.id,
            reaction_type=AnswerEntityReactionTypesEnum.TRIGGER,
        )
        trigger_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(
            db, trigger_answer_handler.member_service.chat.id
        )
        trigger_answer_handler.message_service.message.text = "concrete_key"

        result = await trigger_answer_handler.process()

        assert isinstance(result, TextAnswerSchema)
        assert result.text == "my_concrete_value"

    async def test_chance(
        self,
        db,
        substring_answer_handler,
        prepare_data,
        text_entity_factory,
        based_pack,
    ):
        based_pack.answer_chance = 0
        await AnswerPack.async_add(db, instance=based_pack)
        substring_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(
            db,
            substring_answer_handler.member_service.chat.id,
        )
        with pytest.raises(NextStepException) as error:
            await substring_answer_handler.process()
        assert error.value.args[0] == "Пропуск ответа по проценту срабатывания"

    async def test_edited(
        self,
        db,
        substring_answer_handler,
        prepare_data,
        text_entity_factory,
        based_pack,
        edited_message_service,
    ):
        substring_answer_handler.message_service = edited_message_service
        with pytest.raises(NextStepException) as error:
            await substring_answer_handler.process()
        assert error.value.args[0] == "Пропуск отредактированного сообщения"
