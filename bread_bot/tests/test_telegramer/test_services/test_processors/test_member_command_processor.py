import json

import pytest
import respx
from httpx import Response

from bread_bot.telegramer.models import Chat, ChatToMember
from bread_bot.telegramer.schemas.telegram_messages import ChatMemberBodySchema, MemberSchema
from bread_bot.telegramer.services.processors import MemberCommandMessageProcessor
from bread_bot.telegramer.utils.structs import StatsEnum


class TestMemberCommandProcessor:
    @pytest.fixture
    async def processor(self, message_service, member_service) -> MemberCommandMessageProcessor:
        processor = MemberCommandMessageProcessor(message_service=message_service, member_service=member_service)
        return processor

    @respx.mock
    async def test_get_members(self, db, processor, member_factory):
        members = ChatMemberBodySchema(
            **{'result': [
                {'user': {'id': 1234, 'is_bot': False, 'username': 'uname1'}},
                {'user': {'id': 1235, 'is_bot': False, 'username': 'uname2'}},
                {'user': {'id': 1237, 'is_bot': False, 'username': 'uname3'}},
                {'user': {'id': 1237, 'is_bot': False, 'username': 'lol kek'}},
                {'user': {'id': 7777111, 'is_bot': False, 'username': 'ACTUAL'}},
            ]}
        )
        content = members.dict()
        content['ok'] = True
        response = respx. \
            post('https://api.telegram.org/bot/getChatAdministrators'). \
            mock(
            return_value=Response(
                status_code=200,
                content=json.dumps(content))
        )
        chat = await Chat.async_first(
            db=db,
            where=Chat.id == processor.chat.id,
            select_in_load=Chat.members
        )
        ex_member = await member_factory(
            username="username4",
            member_id="7777111",
        )
        chat.members.append(ChatToMember(chat_id=chat.id, member_id=ex_member.id))
        await chat.commit(db=db)

        members = await processor.get_members()
        assert response.called

        request = response.calls.last.request.read().decode(encoding='utf-8')
        assert json.loads(request) == {'chat_id': processor.message.chat.id}
        assert MemberSchema(
            is_bot=processor.member.is_bot,
            username=processor.member.username,
            first_name=processor.member.first_name,
            last_name=processor.member.last_name,
            id=processor.member.member_id,
        ) in members
        member_schemas_expected = [
            MemberSchema(**{'id': 1234, 'is_bot': False, 'username': 'uname1'}),
            MemberSchema(**{'id': 1235, 'is_bot': False, 'username': 'uname2'}),
            MemberSchema(**{'id': 1237, 'is_bot': False, 'username': 'lol kek'}),
            MemberSchema(**{'id': 7777111, 'is_bot': False, 'username': 'ACTUAL'}),
            MemberSchema(
                is_bot=processor.member.is_bot,
                username=processor.member.username,
                first_name=processor.member.first_name,
                last_name=processor.member.last_name,
                id=processor.member.member_id,
            ),
        ]
        assert member_schemas_expected == members

    async def test_top(self, mocker, processor):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        test_member_two = MemberSchema(
            id=2,
            is_bot=False,
            first_name='Bill',
            last_name='Martin',
            username='somebill'
        )
        mock_members = mocker.patch.object(MemberCommandMessageProcessor, "get_members",
                                           return_value=[test_member, test_member_two, None])
        processor.chat.chat_id = -11111
        processor.command_params = "Some param"
        processor.message.text = "Хлеб топ чуваков"

        result = await processor.process()
        assert f"{test_member.first_name} {test_member.last_name}" in result.text
        assert f"{test_member_two.first_name} {test_member_two.last_name}" in result.text
        mock_members.assert_called_once()

    async def test_who_is(self, mocker, processor):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        mocker.patch.object(MemberCommandMessageProcessor, "get_members",
                            return_value=[test_member, ])
        processor.message.text = "Хлеб кто чувак"
        processor.chat.chat_id = 1111
        result = await processor.process()
        assert f"{processor.message.source.first_name} {processor.message.source.last_name}" in result.text

        processor.chat.chat_id = -1111
        result = await processor.process()
        assert f"{test_member.first_name} {test_member.last_name}" in result.text

    async def test_couple_members(self, mocker, processor):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        test_member_two = MemberSchema(
            id=2,
            is_bot=False,
            first_name='Bill',
            last_name='Martin',
            username='somebill'
        )
        mocker.patch.object(MemberCommandMessageProcessor, "get_members", return_value=[test_member, test_member_two])
        processor.message.text = "Хлеб парочка"

        processor.chat.chat_id = -1111
        result = await processor.process()
        assert f"{test_member.first_name} {test_member.last_name}" in result.text
        assert f"{test_member_two.first_name} {test_member_two.last_name}" in result.text

    async def test_show_stats(self, processor, stats_factory):
        await stats_factory(slug=StatsEnum.FLUDER.name,
                            member_id=processor.member.id,
                            chat_id=processor.chat.chat_id,
                            count=8)
        await stats_factory(slug=StatsEnum.CATCH_TRIGGER.name,
                            member_id=processor.member.id,
                            chat_id=processor.chat.chat_id,
                            count=10)
        processor.message.text = "Хлеб стата"
        result = await processor.process()
        assert result.text == "Попался на триггер:\nTester Testerov - 10\n\n\n" \
                              "Написал сообщение:\nTester Testerov - 9\n\n\n" \
                              "Вызвал бота:\nTester Testerov - 1\n\n\n"
