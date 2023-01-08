import pytest

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.models import AnswerPack, AnswerPacksToChats
from bread_bot.common.schemas.bread_bot_answers import (
    TextAnswerSchema,
    StickerAnswerSchema,
    VoiceAnswerSchema,
    PhotoAnswerSchema,
    GifAnswerSchema,
)
from bread_bot.common.services.handlers.answer_handler import SubstringAnswerHandler, TriggerAnswerHandler
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

    @pytest.mark.parametrize(
        "key, message_text",
        [
            ("слова", "слово"),
            ("слова", "слову"),
            ("слова", "в слове"),
            ("слова", "словах"),
            ("слова", "у слова"),
            ("слова", "слов"),
            ("Ваня", "Ване"),
            ("Нурислам", "Нурисламы"),
            ("Нурисламы", "Нурислам"),
            ("Нурисламы", "Нурисламу"),
            ("ручка", "ручке"),
            ("сделать", "сделать"),
            ("some_en_key", "some_en_key"),
            ("зарифовое", "зарифовая"),
        ]
    )
    async def test_process_lemma_substring(
        self, db, substring_answer_handler, based_pack, text_entity_factory, key, message_text
    ):
        await text_entity_factory(
            key=key, value="value", reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING, pack_id=based_pack.id
        )
        substring_answer_handler.default_answer_pack = await AnswerPack.get_by_chat_id(
            db, substring_answer_handler.member_service.chat.id
        )
        substring_answer_handler.message_service.message.text = f"Есть лемма {message_text} в предложении"

        result = await substring_answer_handler.process()

        assert isinstance(result, TextAnswerSchema)
        assert result.text == "value"

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
