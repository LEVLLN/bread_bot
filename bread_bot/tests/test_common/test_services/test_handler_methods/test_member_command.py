import json

import pytest
import respx
from httpx import Response

from bread_bot.common.exceptions.base import RaiseUpException
from bread_bot.common.models import (
    AnswerPack,
    AnswerPacksToChats,
    Chat, ChatToMember,
)
from bread_bot.common.schemas.commands import (
    CommandSchema,
)
from bread_bot.common.schemas.telegram_messages import ChatMemberBodySchema, MemberSchema
from bread_bot.common.services.handlers.command_methods.member_command_method import MemberCommandMethod
from bread_bot.common.utils.structs import MemberCommandsEnum


class TestMemberCommands:
    @pytest.fixture
    async def command_instance(self, ):
        yield CommandSchema(
            header="хлеб",
            command=MemberCommandsEnum.WHO,
            raw_command="кто",
            rest_text="Some text?"
        )

    @pytest.fixture
    async def based_pack(self, db, member_command_method):
        answer_pack = await AnswerPack.async_add(db, instance=AnswerPack())
        await AnswerPacksToChats.async_add(
            db=db,
            instance=AnswerPacksToChats(
                chat_id=member_command_method.member_service.chat.id,
                pack_id=answer_pack.id,
            )
        )
        yield answer_pack

    @pytest.fixture
    async def member_command_method(
            self,
            db,
            message_service,
            member_service,
            command_instance,
    ):
        member_command_method = MemberCommandMethod(
            db=db,
            member_service=member_service,
            message_service=message_service,
            command_instance=command_instance,
        )
        member_command_method.member_service.chat.chat_id = -10000
        yield member_command_method

    @pytest.fixture
    def member_content_list(self, member_service):
        return [
            {"user": {"id": member_service.member.member_id,
                      "is_bot": False, "username": "uname1", "first_name": "Atest", "last_name": "Atestov"}},
            {"user": {"id": 1235, "is_bot": False, "username": "uname2",
                      "first_name": "Btest", "last_name": "Btestov"}},
            {"user": {"id": 1237, "is_bot": False, "username": "uname3",
                      "first_name": "Ctest", "last_name": "Ctestov"}},
            {"user": {"id": 1237, "is_bot": False, "username": "lol kek",
                      "first_name": "Dtest", "last_name": "Dtestov"}},
            {"user": {"id": 7777111, "is_bot": False, "username": "ACTUAL",
                      "first_name": "Etest", "last_name": "Etestov"}},
        ]

    @pytest.fixture
    async def member_content_response_mock(self, member_content_list):
        members = ChatMemberBodySchema(
            **{'result': member_content_list}
        )
        content = members.dict()
        content['ok'] = True
        return respx. \
            post('https://api.telegram.org/bot/getChatAdministrators'). \
            mock(
            return_value=Response(
                status_code=200,
                content=json.dumps(content))
        )

    @pytest.fixture
    async def ex_member_add(self, db, member_service, member_factory):
        chat = await Chat.async_first(
            db=db,
            where=Chat.id == member_service.chat.id,
            select_in_load=Chat.members
        )
        ex_member = await member_factory(
            username="username4",
            member_id="7777111",
            first_name="ex_exists",
            last_name="ex_existsov"
        )
        chat.members.append(ChatToMember(chat_id=chat.id, member_id=ex_member.id))
        await chat.commit(db=db)
        yield ex_member

    @pytest.fixture
    async def administrators_members(self, member_content_list):
        yield {
            params["user"]["id"]: MemberSchema(**params["user"])
            for params in member_content_list
        }

    @respx.mock
    async def test_get_admin_members(self, member_command_method, member_content_response_mock, member_content_list):
        response = member_content_response_mock

        result = await member_command_method._get_admin_members()
        assert response.called

        assert result == {params["user"]["id"]: MemberSchema(**params["user"]) for params in member_content_list}

    async def test_get_member_from_db(self, member_command_method, ex_member_add):
        result = await member_command_method._get_chat_members()

        default_member = member_command_method.member_service.member
        assert result == {
            member.member_id: MemberSchema(
                is_bot=member.is_bot,
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name,
                id=member.member_id,
            ) for member in [default_member, ex_member_add]
        }

    async def test_get_members(self, mocker, member_command_method, member_content_list, ex_member_add):
        get_admin_members_result = {
            params["user"]["id"]: MemberSchema(**params["user"])
            for params in member_content_list
        }
        mocker.patch.object(MemberCommandMethod, "_get_admin_members", return_value=get_admin_members_result)

        result = await member_command_method.get_members()

        assert result == [
            MemberSchema(**member_content_list[0]["user"]),
            MemberSchema(**member_content_list[4]["user"]),
            MemberSchema(**member_content_list[1]["user"]),
            MemberSchema(**member_content_list[3]["user"]),
        ]

    async def test_get_one_of_group(
            self,
            mocker,
            member_command_method,
            member_content_list,
            administrators_members,
            ex_member_add,
    ):
        member_command_method.member_service.chat.chat_id = -10000
        mocker.patch.object(MemberCommandMethod, "_get_admin_members", return_value=administrators_members)

        result = await member_command_method.get_one_of_group()
        assert result in [member.first_name + " " + member.last_name for member in
                          (MemberSchema(**member_content_list[0]["user"]),
                           MemberSchema(**member_content_list[4]["user"]),
                           MemberSchema(**member_content_list[1]["user"]),
                           MemberSchema(**member_content_list[3]["user"]),)]

    async def test_get_one_of_group_in_private(
            self,
            mocker,
            member_command_method,
            member_content_list,
            ex_member_add,
    ):
        member_command_method.member_service.chat.chat_id = 10000
        get_admin_members_result = {
            params["user"]["id"]: MemberSchema(**params["user"])
            for params in member_content_list
        }
        mocker.patch.object(MemberCommandMethod, "_get_admin_members", return_value=get_admin_members_result)

        result = await member_command_method.get_one_of_group()
        member = member_command_method.member_service.member

        assert result == member.first_name + " " + member.last_name

    @pytest.mark.parametrize(
        "raw_command, expected_result",
        [
            ("кто", "Test Testerov Some text"),
            ("у кого", "Some text у Test Testerov"),
            ("кем", "Some text им: Test Testerov"),
            ("с кем", "Some text с Test Testerov"),
            ("кого", "Some text Test Testerov"),
            ("кому", "Some text ему: Test Testerov"),
            ("о ком", "Some text о Test Testerov"),
            ("чья", "Some text его: Test Testerov"),
            ("чей", "Some text его: Test Testerov"),
            ("чьё", "Some text его: Test Testerov"),
            ("чье", "Some text его: Test Testerov"),
            ("test", "Some text - это Test Testerov"),
        ]
    )
    async def test_who_command(self, mocker, member_command_method, raw_command, expected_result):
        mocker.patch.object(MemberCommandMethod, "get_one_of_group", return_value="Test Testerov")
        member_command_method.command_instance.raw_command = raw_command

        result = await member_command_method.execute()

        assert result.text == expected_result

    async def test_top_command_only_db(self, mocker, member_command_method, ex_member_add):
        member_command_method.command_instance.command = MemberCommandsEnum.TOP
        member_command_method.command_instance.raw_command = "топ"
        mocker.patch.object(MemberCommandMethod, "_get_admin_members", return_value={})

        result = await member_command_method.execute()
        for member in [ex_member_add, member_command_method.member_service.member]:
            assert member.first_name + " " + member.last_name in result.text

    async def test_top_command_with_admins(self, mocker, member_command_method, ex_member_add, administrators_members):
        member_command_method.command_instance.command = MemberCommandsEnum.TOP
        member_command_method.command_instance.raw_command = "топ"
        mocker.patch.object(MemberCommandMethod, "_get_admin_members", return_value=administrators_members)

        result = await member_command_method.execute()
        for member in administrators_members.values():
            assert member.first_name + " " + member.last_name in result.text

    async def test_couple_less_two(self,  mocker, member_command_method, member_content_list):
        member_command_method.command_instance.command = MemberCommandsEnum.COUPLE
        member_command_method.command_instance.raw_command = "парочка"
        member_command_method.command_instance.rest_text = "some test"

        mocker.patch.object(
            MemberCommandMethod,
            "get_members",
            return_value=[MemberSchema(**member_content_list[0]["user"])])
        with pytest.raises(RaiseUpException) as error:
            await member_command_method.execute()
        assert error.value.args[0] == "В группе недостаточно пользователей для образования пары!"

    async def test_couple(self,  mocker, member_command_method, member_content_list):
        member_command_method.command_instance.command = MemberCommandsEnum.COUPLE
        member_command_method.command_instance.raw_command = "парочка"
        member_command_method.command_instance.rest_text = "some test"

        first_member = MemberSchema(**member_content_list[0]["user"])
        second_member = MemberSchema(**member_content_list[1]["user"])
        mocker.patch.object(
            MemberCommandMethod,
            "get_members",
            return_value=[
                first_member, second_member
            ]
        )
        result = await member_command_method.execute()
        assert first_member.first_name + " " + first_member.last_name in result.text
        assert second_member.first_name + " " + second_member.last_name in result.text
        assert result.text.startswith("Парочку some test образовали")
