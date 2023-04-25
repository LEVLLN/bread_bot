import pytest
from sqlalchemy import and_

from bread_bot.common.exceptions.base import RaiseUpException
from bread_bot.common.models import (
    AnswerPack,
    AnswerPacksToChats,
    AnswerEntity,
    Chat,
)
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.schemas.commands import (
    KeyValueParameterCommandSchema,
    ValueListCommandSchema,
    ValueParameterCommandSchema,
    CommandSchema,
    ValueCommandSchema,
)
from bread_bot.common.services.handlers.command_methods.admin_command_method import AdminCommandMethod
from bread_bot.common.services.messages.message_service import MessageService
from bread_bot.common.utils.structs import (
    AdminCommandsEnum,
    CommandAnswerParametersEnum,
    AnswerEntityReactionTypesEnum,
    ANSWER_ENTITY_MAP,
    AnswerEntityContentTypesEnum,
)


class BaseAdminCommand:
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
    async def admin_command_method(
        self,
        db,
        message_service,
        member_service,
        command_instance,
        based_pack,
    ):
        yield AdminCommandMethod(
            db=db,
            member_service=member_service,
            message_service=message_service,
            command_instance=command_instance,
            default_answer_pack=based_pack,
        )

    @pytest.fixture
    async def admin_command_method_without_pack(
        self,
        db,
        message_service,
        member_service,
        command_instance,
    ):
        yield AdminCommandMethod(
            db=db,
            member_service=member_service,
            message_service=message_service,
            command_instance=command_instance,
            default_answer_pack=None,
        )


class TestAdd(BaseAdminCommand):
    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield KeyValueParameterCommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.ADD,
            parameter=CommandAnswerParametersEnum.TRIGGER,
            key="my_key",
            value="my_value",
            raw_command="добавь",
        )

    @pytest.fixture
    async def text_answer_entity(self, db, based_pack, member_service, admin_command_method):
        yield await AnswerEntity.async_add(
            db=db,
            instance=AnswerEntity(
                key=admin_command_method.command_instance.key,
                value=admin_command_method.command_instance.value,
                reaction_type="TRIGGER",
                pack_id=based_pack.id,
                content_type=AnswerEntityContentTypesEnum.TEXT,
            ),
        )

    async def test_raise_condition(
        self,
        admin_command_method,
        command_instance,
    ):
        admin_command_method.command_instance.parameter = CommandAnswerParametersEnum.SUBSTRING
        command_instance.key = "1"
        admin_command_method.command_instance = command_instance

        with pytest.raises(RaiseUpException) as e:
            await admin_command_method.execute()
        assert e.value.args[0] == "Ключ для подстроки не может быть меньше 3-х символов"

    async def test_existed_packs(self, db, based_pack, mocker, admin_command_method):
        create_mocker = mocker.spy(AnswerPack, "async_add")
        result = await admin_command_method.execute()

        answer_pack = await AnswerPack.get_by_chat_id(db, admin_command_method.member_service.chat.id)
        text_entity = await AnswerEntity.async_first(db=db, where=and_(AnswerEntity.pack_id == answer_pack.id))

        assert answer_pack
        assert text_entity.key == admin_command_method.command_instance.key
        assert text_entity.value == admin_command_method.command_instance.value
        assert text_entity.reaction_type == "TRIGGER"
        assert result.text in admin_command_method.COMPLETE_MESSAGES
        create_mocker.assert_not_called()

    async def test_not_existed_packs(self, db, mocker, admin_command_method_without_pack):
        admin_command_method_without_pack.default_answer_pack = None
        create_mocker = mocker.spy(AnswerPack, "async_add")
        result = await admin_command_method_without_pack.execute()

        answer_pack = await AnswerPack.get_by_chat_id(db, admin_command_method_without_pack.member_service.chat.id)
        text_entity = await AnswerEntity.async_first(db=db, where=and_(AnswerEntity.pack_id == answer_pack.id))

        assert answer_pack
        assert text_entity.key == admin_command_method_without_pack.command_instance.key
        assert text_entity.value == admin_command_method_without_pack.command_instance.value
        assert text_entity.reaction_type == "TRIGGER"
        assert result.text in admin_command_method_without_pack.COMPLETE_MESSAGES
        create_mocker.assert_called_once()

    async def test_existed_answer_entity(self, mocker, db, based_pack, text_answer_entity, admin_command_method):
        create_mocker = mocker.spy(AnswerEntity, "async_add")
        result = await admin_command_method.execute()

        answer_pack = await AnswerPack.get_by_chat_id(db, admin_command_method.member_service.chat.id)
        text_answer_entity = await AnswerEntity.async_first(
            db=db,
            where=and_(
                AnswerEntity.pack_id == answer_pack.id,
                AnswerEntity.content_type == AnswerEntityContentTypesEnum.TEXT,
            ),
        )

        create_mocker.assert_not_called()
        assert text_answer_entity == text_answer_entity
        assert result.text in admin_command_method.COMPLETE_MESSAGES

    async def test_not_existed_answer_entity(self, mocker, db, based_pack, admin_command_method):
        create_mocker = mocker.spy(AnswerEntity, "async_add")
        result = await admin_command_method.execute()

        answer_pack = await AnswerPack.get_by_chat_id(db, admin_command_method.member_service.chat.id)
        text_answer_entity = await AnswerEntity.async_first(db=db, where=and_(AnswerEntity.pack_id == answer_pack.id))

        create_mocker.assert_called_once()
        assert text_answer_entity == text_answer_entity
        assert result.text in admin_command_method.COMPLETE_MESSAGES


class TestShowKeys(BaseAdminCommand):
    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield CommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.SHOW_KEYS,
            raw_command="покажи ключи",
        )

    @pytest.fixture
    async def photo_message_service(self, request_body_message, reply_photo) -> MessageService:
        message_service = MessageService(request_body=request_body_message)
        message_service.message.reply = reply_photo.message.reply
        yield message_service

    @pytest.fixture
    async def answer_entity(self, db, based_pack, reply_photo):
        return await AnswerEntity.async_add(
            db=db,
            instance=AnswerEntity(
                pack_id=based_pack.id,
                value=reply_photo.message.reply.photo[0].file_id,
                key="my_key",
                reaction_type=AnswerEntityReactionTypesEnum.SUBSTRING,
                content_type=AnswerEntityContentTypesEnum.PICTURE,
            ),
        )

    async def test_photo_reply(
        self, db, based_pack, admin_command_method, command_instance, photo_message_service, answer_entity
    ):
        admin_command_method.message_service = photo_message_service
        admin_command_method.command_instance = command_instance
        result = await admin_command_method.execute()

        assert result.text == "Перечень ключей на значение: [my_key]"


class TestRemember(BaseAdminCommand):
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
            command=AdminCommandsEnum.REMEMBER,
            value_list=["my_value", "my_value1"],
            raw_command="запомни",
        )

    async def test_raise_short_key(
        self,
        admin_command_method,
        command_instance,
        photo_message_service,
    ):
        command_instance.value_list = ["1", "212"]
        admin_command_method.message_service = photo_message_service

        with pytest.raises(RaiseUpException) as e:
            await admin_command_method.execute()
        assert e.value.args[0] == "Ключ для подстроки не может быть меньше 3-х символов"

    async def test_raise_not_reply(
        self,
        admin_command_method,
        command_instance,
    ):
        admin_command_method.command_instance = command_instance
        with pytest.raises(RaiseUpException) as e:
            await admin_command_method.execute()
        assert e.value.args[0] == "Необходимо выбрать сообщение в качестве ответа для обработки"

    @pytest.mark.parametrize(
        "command, reaction_type",
        [
            (AdminCommandsEnum.REMEMBER, AnswerEntityReactionTypesEnum.SUBSTRING),
            (AdminCommandsEnum.REMEMBER_TRIGGER, AnswerEntityReactionTypesEnum.TRIGGER),
        ],
    )
    async def test_photo_reply(
        self,
        db,
        based_pack,
        admin_command_method,
        command_instance,
        photo_message_service,
        command,
        reaction_type,
    ):
        admin_command_method.message_service = photo_message_service
        admin_command_method.command_instance.command = command
        result = await admin_command_method.execute()

        entities = await AnswerEntity.async_filter(
            db,
            where=AnswerEntity.pack_id == based_pack.id,
        )
        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert entities is not None
        assert command_instance.value_list == [entity.key for entity in entities]
        assert photo_message_service.message.reply.photo[0].file_id == entities[0].value
        assert entities[0].reaction_type == reaction_type
        assert entities[0].description is None

    @pytest.mark.parametrize(
        "command, reaction_type",
        [
            (AdminCommandsEnum.REMEMBER, AnswerEntityReactionTypesEnum.SUBSTRING),
            (AdminCommandsEnum.REMEMBER_TRIGGER, AnswerEntityReactionTypesEnum.TRIGGER),
        ],
    )
    async def test_gif_reply(
        self,
        db,
        based_pack,
        admin_command_method,
        command_instance,
        reply_gif,
        command,
        reaction_type,
    ):
        admin_command_method.message_service.message.reply = reply_gif.message.reply
        admin_command_method.command_instance.command = command
        result = await admin_command_method.execute()

        entities = await AnswerEntity.async_filter(
            db,
            where=and_(
                AnswerEntity.pack_id == based_pack.id,
                AnswerEntity.content_type == AnswerEntityContentTypesEnum.ANIMATION,
            ),
        )
        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert entities is not None
        assert command_instance.value_list == [entity.key for entity in entities]
        assert reply_gif.message.reply.animation.file_id == entities[0].value
        assert entities[0].reaction_type == reaction_type

    @pytest.mark.parametrize(
        "command, reaction_type",
        [
            (AdminCommandsEnum.REMEMBER, AnswerEntityReactionTypesEnum.SUBSTRING),
            (AdminCommandsEnum.REMEMBER_TRIGGER, AnswerEntityReactionTypesEnum.TRIGGER),
        ],
    )
    async def test_photo_reply_with_capture(
        self,
        db,
        based_pack,
        admin_command_method,
        command_instance,
        message_service,
        reply_photo_with_caption,
        command,
        reaction_type,
    ):
        message_service.message.reply = reply_photo_with_caption.message.reply
        admin_command_method.message_service = message_service
        admin_command_method.command_instance.command = command
        result = await admin_command_method.execute()

        entities = await AnswerEntity.async_filter(
            db,
            where=and_(
                AnswerEntity.pack_id == based_pack.id,
                AnswerEntity.content_type == AnswerEntityContentTypesEnum.PICTURE,
            ),
        )
        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert entities is not None
        assert command_instance.value_list == [entity.key for entity in entities]
        assert message_service.message.reply.photo[0].file_id == entities[0].value
        assert entities[0].reaction_type == reaction_type
        assert entities[0].description == reply_photo_with_caption.message.reply.caption

    @pytest.mark.parametrize(
        "command, reaction_type",
        [
            (AdminCommandsEnum.REMEMBER, AnswerEntityReactionTypesEnum.SUBSTRING),
            (AdminCommandsEnum.REMEMBER_TRIGGER, AnswerEntityReactionTypesEnum.TRIGGER),
        ],
    )
    async def test_voice_reply(
        self,
        db,
        based_pack,
        admin_command_method,
        command_instance,
        reply_voice,
        command,
        reaction_type,
    ):
        admin_command_method.message_service.message.reply = reply_voice.message.reply
        admin_command_method.command_instance.command = command
        result = await admin_command_method.execute()

        entities = await AnswerEntity.async_filter(
            db,
            where=and_(
                AnswerEntity.pack_id == based_pack.id, AnswerEntity.content_type == AnswerEntityContentTypesEnum.VOICE
            ),
        )
        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert entities is not None
        assert command_instance.value_list == [entity.key for entity in entities]
        assert reply_voice.message.reply.voice.file_id == entities[0].value
        assert entities[0].reaction_type == reaction_type

    @pytest.mark.parametrize(
        "command, reaction_type",
        [
            (AdminCommandsEnum.REMEMBER, AnswerEntityReactionTypesEnum.SUBSTRING),
            (AdminCommandsEnum.REMEMBER_TRIGGER, AnswerEntityReactionTypesEnum.TRIGGER),
        ],
    )
    async def test_sticker_reply(
        self,
        db,
        based_pack,
        admin_command_method,
        command_instance,
        reply_sticker,
        command,
        reaction_type,
    ):
        admin_command_method.message_service.message.reply = reply_sticker.message.reply
        admin_command_method.command_instance.command = command
        result = await admin_command_method.execute()

        entities = await AnswerEntity.async_filter(
            db,
            where=and_(
                AnswerEntity.pack_id == based_pack.id, AnswerEntity.content_type == AnswerEntityContentTypesEnum.STICKER
            ),
        )
        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert entities is not None
        assert command_instance.value_list == [entity.key for entity in entities]
        assert reply_sticker.message.reply.sticker.file_id == entities[0].value
        assert entities[0].reaction_type == reaction_type

    @pytest.mark.parametrize(
        "command, reaction_type",
        [
            (AdminCommandsEnum.REMEMBER, AnswerEntityReactionTypesEnum.SUBSTRING),
            (AdminCommandsEnum.REMEMBER_TRIGGER, AnswerEntityReactionTypesEnum.TRIGGER),
        ],
    )
    async def test_repeat_keys(
        self,
        db,
        based_pack,
        admin_command_method,
        command_instance,
        reply_sticker,
        command,
        reaction_type,
    ):
        admin_command_method.message_service.message.reply = reply_sticker.message.reply
        admin_command_method.command_instance.command = command
        result = await admin_command_method.execute()
        entities = await AnswerEntity.async_filter(
            db,
            where=and_(
                AnswerEntity.pack_id == based_pack.id, AnswerEntity.content_type == AnswerEntityContentTypesEnum.STICKER
            ),
        )
        assert len(entities) == 2
        result = await admin_command_method.execute()
        entities = await AnswerEntity.async_filter(
            db,
            where=AnswerEntity.pack_id == based_pack.id,
        )
        assert len(entities) == 2


@pytest.mark.skip
class TestDelete(BaseAdminCommand):
    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield ValueParameterCommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.DELETE,
            parameter=CommandAnswerParametersEnum.SUBSTRING,
            value="LOL",
            raw_command="удали",
        )

    @pytest.fixture
    async def command_key_value_instance(
        self,
    ):
        yield KeyValueParameterCommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.DELETE,
            parameter=CommandAnswerParametersEnum.SUBSTRING,
            key="TEST",
            value="LOL",
            raw_command="удали",
        )

    async def test_not_existed_packs(self, db, admin_command_method, command_instance):
        admin_command_method.default_answer_pack = None
        result = await admin_command_method.execute()
        assert result.text == "У чата нет ни одного пакета под управлением"

    @pytest.mark.parametrize(
        "expected_model",
        [
            AnswerEntity,
        ],
    )
    @pytest.mark.parametrize(
        "content_type",
        [
            AnswerEntityContentTypesEnum.TEXT,
            AnswerEntityContentTypesEnum.STICKER,
            AnswerEntityContentTypesEnum.VOICE,
            AnswerEntityContentTypesEnum.PICTURE,
        ],
    )
    @pytest.mark.parametrize(
        "parameter",
        [
            CommandAnswerParametersEnum.SUBSTRING_LIST,
            CommandAnswerParametersEnum.SUBSTRING,
            CommandAnswerParametersEnum.TRIGGER,
            CommandAnswerParametersEnum.TRIGGER_LIST,
        ],
    )
    async def test(
        self, db, admin_command_method, command_instance, based_pack, expected_model, parameter, content_type
    ):
        admin_command_method.command_instance.parameter = parameter
        entities = []
        for key in ["other_key", command_instance.value]:
            entities.append(
                expected_model(
                    key=key,
                    value="something",
                    reaction_type=ANSWER_ENTITY_MAP[parameter],
                    pack_id=based_pack.id,
                    content_type=content_type,
                )
            )
        await expected_model.async_add_all(db, entities)

        pre_expected = await expected_model.async_filter(db, where=expected_model.pack_id == based_pack.id)
        assert len(pre_expected) == 2
        assert pre_expected == entities

        result = await admin_command_method.execute()
        expected = await expected_model.async_filter(
            db, where=and_(expected_model.pack_id == based_pack.id, expected_model.content_type == content_type)
        )

        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert len(expected) == 1
        assert expected[0].key == "other_key"
        assert expected[0].reaction_type == ANSWER_ENTITY_MAP[parameter]
        assert expected[0].pack_id == based_pack.id

    async def test_key_value(
        self,
        db,
        admin_command_method,
        command_key_value_instance,
        based_pack,
    ):
        admin_command_method.command_instance = command_key_value_instance
        admin_command_method.default_answer_pack = based_pack
        entity = AnswerEntity(
            key=command_key_value_instance.key,
            value=command_key_value_instance.value,
            reaction_type=ANSWER_ENTITY_MAP[command_key_value_instance.parameter],
            pack_id=based_pack.id,
            content_type=AnswerEntityContentTypesEnum.TEXT,
        )
        await AnswerEntity.async_add(db, entity)

        assert (
            await AnswerEntity.async_first(
                db,
            )
            == entity
        )
        result = await admin_command_method.execute()
        expected = await AnswerEntity.async_filter(db, where=AnswerEntity.pack_id == based_pack.id)

        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert expected == []


class TestAnswerChance(BaseAdminCommand):
    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield CommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.ANSWER_CHANCE,
            raw_command="процент",
        )

    @pytest.fixture
    async def command_value_instance(
        self,
    ):
        yield ValueCommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.ANSWER_CHANCE,
            value="100",
            raw_command="процент",
        )

    @pytest.mark.parametrize(
        "answer_chance",
        [
            "100",
            "20",
            "80",
            "15",
        ],
    )
    async def test_set_answer_chance(
        self,
        db,
        admin_command_method,
        command_value_instance,
        based_pack,
        answer_chance,
    ):
        command_value_instance.value = answer_chance
        admin_command_method.command_instance = command_value_instance
        admin_command_method.default_answer_pack = based_pack
        assert based_pack.answer_chance == 100

        result = await admin_command_method.execute()
        excepted_answer_pack = await AnswerPack.async_first(db=db, where=AnswerPack.id == based_pack.id)

        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert excepted_answer_pack.answer_chance == int(answer_chance)

    @pytest.mark.parametrize(
        "answer_chance",
        [
            "100",
            "20",
            "80",
            "15",
        ],
    )
    async def test_get_answer_chance(
        self,
        db,
        admin_command_method,
        command_instance,
        based_pack,
        answer_chance,
    ):
        based_pack.answer_chance = answer_chance
        await AnswerPack.async_add(db, based_pack)
        admin_command_method.command_instance = command_instance
        admin_command_method.default_answer_pack = based_pack

        result = await admin_command_method.execute()

        assert result.text == answer_chance

    @pytest.mark.parametrize(
        "answer_chance",
        [
            "some_string",
            "-1",
            "0.11",
            "101",
            "140",
            "100.1",
            "",
            None,
        ],
    )
    async def test_invalid_value(
        self,
        db,
        admin_command_method,
        command_value_instance,
        based_pack,
        answer_chance,
    ):
        command_value_instance.value = answer_chance
        admin_command_method.command_instance = command_value_instance
        assert based_pack.answer_chance == 100

        with pytest.raises(RaiseUpException) as error:
            await admin_command_method.execute()

        excepted_answer_pack = await AnswerPack.async_first(db=db, where=AnswerPack.id == based_pack.id)

        assert error.value.args[0] == "Некорректное значение. Необходимо ввести число от 0 до 100"
        assert excepted_answer_pack.answer_chance == 100


class TestCheckAnswer(BaseAdminCommand):
    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield ValueCommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.CHECK_ANSWER,
            value="my_substring",
            raw_command="проверка",
        )

    @pytest.mark.parametrize("answer_chance", [0, 100])
    @pytest.mark.parametrize(
        "reaction_type", [AnswerEntityReactionTypesEnum.SUBSTRING, AnswerEntityReactionTypesEnum.TRIGGER]
    )
    async def test_existed_substring(
        self, db, admin_command_method, based_pack, command_instance, text_entity_factory, answer_chance, reaction_type
    ):
        based_pack.answer_chance = answer_chance
        await AnswerPack.async_add(db, based_pack)
        await text_entity_factory(
            key="my_substring",
            value="my_value",
            reaction_type=reaction_type,
            pack_id=based_pack.id,
        )

        admin_command_method.command_instance = command_instance
        result = await admin_command_method.execute()
        assert isinstance(result, TextAnswerSchema)
        assert result.text == "my_value"

    @pytest.mark.parametrize("answer_chance", [0, 100])
    @pytest.mark.parametrize(
        "reaction_type", [AnswerEntityReactionTypesEnum.SUBSTRING, AnswerEntityReactionTypesEnum.TRIGGER]
    )
    async def test_existed_substring(
        self, db, admin_command_method, based_pack, command_instance, answer_chance, reaction_type
    ):
        based_pack.answer_chance = answer_chance
        await AnswerPack.async_add(db, based_pack)

        admin_command_method.command_instance = command_instance
        result = await admin_command_method.execute()
        assert isinstance(result, TextAnswerSchema)
        assert result.text == "Ничего не было найдено"

    async def test_another_command(self, admin_command_method):
        command = CommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.CHECK_ANSWER,
            raw_command="проверка",
        )
        admin_command_method.command_instance = command
        result = await admin_command_method.execute()
        assert isinstance(result, TextAnswerSchema)
        assert result.text == "Необходимо указать параметром, что надо искать"


class TestSay(BaseAdminCommand):
    async def test_another_command(self, admin_command_method):
        command = CommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.SAY,
            raw_command="скажи",
        )
        admin_command_method.command_instance = command
        result = await admin_command_method.execute()
        assert isinstance(result, TextAnswerSchema)
        assert result.text == "Необходимо указать параметром, что надо сказать"

    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield ValueCommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.SAY,
            value="my_value",
            raw_command="скажи",
        )

    async def test_existed_substring(
        self,
        db,
        admin_command_method,
        based_pack,
        command_instance,
        text_entity_factory,
    ):
        admin_command_method.command_instance = command_instance
        result = await admin_command_method.execute()
        assert isinstance(result, TextAnswerSchema)
        assert result.text == "my_value"


class TestMorphAnswerChance(BaseAdminCommand):
    @pytest.fixture
    async def command_instance(
        self,
    ):
        yield CommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.MORPH_ANSWER_CHANCE,
            raw_command="процент бреда",
        )

    @pytest.fixture
    async def command_value_instance(
        self,
    ):
        yield ValueCommandSchema(
            header="хлеб",
            command=AdminCommandsEnum.MORPH_ANSWER_CHANCE,
            value="100",
            raw_command="процент бреда 100",
        )

    @pytest.mark.parametrize(
        "answer_chance",
        [
            "100",
            "20",
            "80",
            "15",
        ],
    )
    async def test_set_morph_answer_chance(
        self,
        db,
        admin_command_method,
        command_value_instance,
        based_pack,
        answer_chance,
    ):
        command_value_instance.value = answer_chance
        admin_command_method.command_instance = command_value_instance
        assert based_pack.answer_chance == 100

        result = await admin_command_method.execute()
        excepted_answer_pack = await Chat.async_first(
            db=db, where=Chat.id == admin_command_method.member_service.chat.id
        )

        assert result.text in admin_command_method.COMPLETE_MESSAGES
        assert excepted_answer_pack.morph_answer_chance == int(answer_chance)

    @pytest.mark.parametrize(
        "answer_chance",
        [
            "100",
            "20",
            "80",
            "15",
        ],
    )
    async def test_get_answer_chance(
        self,
        db,
        admin_command_method,
        command_instance,
        based_pack,
        answer_chance,
    ):
        admin_command_method.member_service.chat.morph_answer_chance = answer_chance
        await Chat.async_add(db, admin_command_method.member_service.chat)
        admin_command_method.command_instance = command_instance

        result = await admin_command_method.execute()

        assert result.text == answer_chance

    @pytest.mark.parametrize(
        "answer_chance",
        [
            "some_string",
            "-1",
            "0.11",
            "101",
            "140",
            "100.1",
            "",
            None,
        ],
    )
    async def test_invalid_value(
        self,
        db,
        admin_command_method,
        command_value_instance,
        based_pack,
        answer_chance,
    ):
        command_value_instance.value = answer_chance
        admin_command_method.command_instance = command_value_instance
        assert admin_command_method.member_service.chat.morph_answer_chance == 100

        with pytest.raises(RaiseUpException) as error:
            await admin_command_method.execute()

        excepted_answer_pack = await Chat.async_first(
            db=db, where=Chat.id == admin_command_method.member_service.chat.id
        )
        assert error.value.args[0] == "Некорректное значение. Необходимо ввести число от 0 до 100"
        assert excepted_answer_pack.morph_answer_chance == 100
