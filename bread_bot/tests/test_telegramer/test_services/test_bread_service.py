import asyncio
import json
import unittest

import respx
from httpx import Response
from sqlalchemy import and_

from bread_bot.telegramer.models import Member, \
    LocalMeme, Chat, ChatToMember, Stats
from bread_bot.telegramer.schemas.telegram_messages import \
    StandardBodySchema, \
    ChatMemberBodySchema
from bread_bot.telegramer.services.bread_service import BreadService
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum
from bread_bot.utils.testing_tools import init_async_session


class BreadServiceTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.telegram_client = TelegramClient()
        cls.default_return_value = Response(
            status_code=200,
            content=json.dumps({'some_key': 'some_value'})
        )
        cls.default_message = StandardBodySchema(
            **{
                'update_id': 123,
                'message': {
                    'message_id': 1,
                    'from': {
                        'id': 134,
                        'is_bot': False,
                        'first_name': 'Tester',
                        'last_name': 'Testerov',
                        'username': 'Test_test',
                        'language_code': 'ru'
                    },
                    'chat': {
                        'id': 134,
                        'first_name': 'Tester',
                        'last_name': 'Testerov',
                        'username': 'Test_test',
                        'type': 'private'
                    },
                    'date': 12343,
                    'text': 'Test'
                }
            }
        )
        asyncio.run(LocalMeme.async_add(
            db=cls.session,
            instance=LocalMeme(
                type=LocalMemeTypesEnum.FREE_WORDS.name,
                data={
                    'some free word str': 'value',
                    'some_free_word': ['default answer'],
                    'some free word 3': {'default answer': 'value'},
                    'some free word 2': ['default answer']
                },
                chat_id=cls.default_message.message.chat.id,
            )
        ))
        asyncio.run(
            LocalMeme.async_add(
                db=cls.session,
                instance=LocalMeme(
                    type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
                    data={
                        'my_substring': ['some_answer'],
                        'my_str': 'some_answer',
                    },
                    chat_id=cls.default_message.message.chat.id,
                )
            )
        )
        local_meme_name_instance = LocalMeme(
            type=LocalMemeTypesEnum.MEME_NAMES.name,
            chat_id=cls.default_message.message.chat.id,
            data={
                'test_command': ['test_result'],
            }
        )
        asyncio.run(
            LocalMeme.async_add(
                db=cls.session,
                instance=local_meme_name_instance,
            )

        )

    async def test_handle_chat_create(self):
        message = self.default_message.copy(deep=True)
        message.message.chat.title = 'Some Chat'
        message.message.chat.id = 12345

        self.assertIsNone(
            await Chat.async_first(
                db=self.session,
                filter_expression=Chat.chat_id == message.message.chat.id)
        )
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        chat = \
            await bread_service.handle_chat()
        self.assertEqual(
            await Chat.async_first(
                db=self.session,
                filter_expression=Chat.chat_id == message.message.chat.id
            ),
            chat
        )
        self.assertEqual(
            chat.name,
            message.message.chat.title,
        )

    async def test_handle_chat_update_title(self):
        message = self.default_message.copy(deep=True)
        message.message.chat.title = 'Testing'
        message.message.chat.id = 3333
        chat_instance = Chat(
            chat_id=message.message.chat.id,
            name=message.message.chat.title,
        )
        chat = await Chat.async_add(
            db=self.session,
            instance=chat_instance
        )
        self.assertIsNotNone(
            await Chat.async_first(
                db=self.session,
                filter_expression=Chat.chat_id == message.message.chat.id)
        )
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        chat.name = 'Tooling'
        chat = \
            await bread_service.handle_chat()
        self.assertEqual(
            await Chat.async_first(
                db=self.session,
                filter_expression=Chat.chat_id == message.message.chat.id
            ),
            chat
        )
        self.assertEqual(
            chat.name,
            'Testing'
        )

    async def test_handle_member_create(self):
        message = self.default_message.copy(deep=True)
        message.message.source.username = 'Toster'
        filter_param = Member.username == message.message.source.username
        self.assertIsNone(
            await Member.async_first(
                db=self.session,
                filter_expression=filter_param
            )
        )
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        member = \
            await bread_service.handle_member(member=message.message.source)
        self.assertEqual(
            await Member.async_first(
                db=self.session,
                filter_expression=filter_param

            ),
            member
        )

    async def test_handle_member_update(self):
        message = self.default_message.copy(deep=True)
        message.message.source.username = 'test_user'
        member = await Member.async_add(
            db=self.session,
            instance=Member(
                username=message.message.source.username,
            )
        )
        self.assertIsNotNone(
            await Member.async_first(
                db=self.session,
                filter_expression=
                Member.username == message.message.source.username)
        )
        self.assertIsNone(
            member.member_id,
        )
        self.assertIsNone(
            member.first_name,
        )
        self.assertIsNone(
            member.last_name,
        )
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        member = \
            await bread_service.handle_member(member=message.message.source)
        self.assertEqual(
            await Member.async_first(
                db=self.session,
                filter_expression=
                Member.username == message.message.source.username
            ),
            member
        )
        self.assertIsNotNone(
            member.member_id,
        )
        self.assertIsNotNone(
            member.first_name,
        )
        self.assertIsNotNone(
            member.last_name,
        )

    async def test_parse_incoming_message_trigger(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'Хлеб привет'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(bread_service.trigger_word)
        self.assertIsNone(bread_service.command)
        self.assertIsNone(bread_service.params)
        await bread_service.parse_incoming_message()
        self.assertEqual(bread_service.trigger_word, 'Хлеб')
        self.assertEqual(bread_service.params, 'привет')
        self.assertEqual(bread_service.command, '')

    async def test_parse_incoming_message_command(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'Хлеб help'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(bread_service.trigger_word)
        self.assertIsNone(bread_service.command)
        self.assertIsNone(bread_service.params)
        await bread_service.parse_incoming_message()
        self.assertEqual(bread_service.trigger_word, 'Хлеб')
        self.assertEqual(bread_service.params, '')
        self.assertEqual(bread_service.command, 'help')
        # with params
        message = self.default_message.copy(deep=True)
        message.message.text = 'Хлеб help any'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(bread_service.trigger_word)
        self.assertIsNone(bread_service.command)
        self.assertIsNone(bread_service.params)
        await bread_service.parse_incoming_message()
        self.assertEqual(bread_service.trigger_word, 'Хлеб')
        self.assertEqual(bread_service.params, 'any')
        self.assertEqual(bread_service.command, 'help')

    async def test_parse_incoming_message_local_meme(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'Хлеб test_command params'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(bread_service.trigger_word)
        self.assertIsNone(bread_service.command)
        self.assertIsNone(bread_service.params)
        await bread_service.parse_incoming_message()
        self.assertEqual(bread_service.trigger_word, 'Хлеб')
        self.assertEqual(bread_service.params, 'params')
        self.assertEqual(bread_service.command, 'test_command')

    async def test_parse_incoming_message_without_triggers(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'привет'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(bread_service.trigger_word)
        self.assertIsNone(bread_service.params)
        self.assertIsNone(bread_service.command)
        with self.assertRaises(ValueError):
            await bread_service.parse_incoming_message()
        self.assertIsNone(bread_service.trigger_word)
        self.assertIsNone(bread_service.params)
        self.assertIsNone(bread_service.command)

    async def test_handle_chats_to_members_success(self):
        message = self.default_message.copy(deep=True)
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        member = Member(username='Binder')
        chat = Chat(name='BinderGroup', chat_id=20000)
        await Member.async_add(self.session, member)
        await Chat.async_add(self.session, chat)
        await bread_service.handle_chats_to_members(member.id, chat.id)
        chat_to_members = await ChatToMember.async_filter(
            db=self.session,
            filter_expression=and_(
                ChatToMember.chat_id == chat.id,
                ChatToMember.member_id == member.id,
            )
        )
        self.assertIsNotNone(chat_to_members)
        self.assertEqual(len(chat_to_members), 1)
        second_member = Member(username='Binder2')
        await Member.async_add(self.session, second_member)
        await bread_service.handle_chats_to_members(second_member.id, chat.id)
        chat_to_members = await ChatToMember.async_filter(
            db=self.session,
            filter_expression=and_(
                ChatToMember.chat_id == chat.id,
                ChatToMember.member_id.in_([second_member.id, member.id])
            )
        )
        self.assertIsNotNone(chat_to_members)
        self.assertEqual(len(chat_to_members), 2)

    async def test_handle_chats_to_members_empty(self):
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=self.default_message.message,
        )
        await bread_service.handle_chats_to_members(100500, 100500)
        chat_to_members = await ChatToMember.async_filter(
            db=self.session,
            filter_expression=and_(
                ChatToMember.chat_id == 100500,
                ChatToMember.member_id == 100500,
            )
        )
        self.assertListEqual(chat_to_members, [])
        self.assertEqual(len(chat_to_members), 0)

    async def test_count_stats(self):
        member = await Member.async_add(self.session,
                                        Member(username='Statistic'))
        chat = await Chat.async_add(self.session,
                                    Chat(name='StatisticGroup', chat_id=20001))
        message = self.default_message.copy(deep=True)
        message.message.source.username = member.username
        message.message.chat.id = chat.chat_id
        self.assertIsNone(
            await Stats.async_first(
                db=self.session,
                filter_expression=and_(
                    Stats.member_id == member.id,
                    Stats.chat_id == chat.chat_id,
                    Stats.slug == StatsEnum.EDITOR.name,
                )
            )
        )
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        await bread_service.count_stats(member_db=member,
                                        stats_enum=StatsEnum.EDITOR)
        stats = await Stats.async_first(
            db=self.session,
            filter_expression=and_(
                Stats.member_id == member.id,
                Stats.chat_id == chat.chat_id,
                Stats.slug == StatsEnum.EDITOR.name,
            )
        )
        self.assertEqual(
            stats.count,
            1
        )
        await bread_service.count_stats(member_db=member,
                                        stats_enum=StatsEnum.EDITOR)
        self.session.refresh(stats)
        self.assertEqual(
            stats.count,
            2
        )

    async def test_get_unknown_messages(self):
        message = self.default_message.copy(deep=True)
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        result = await bread_service.get_unknown_messages()
        self.assertListEqual(
            result,
            structs.DEFAULT_UNKNOWN_MESSAGE,
        )
        local_memes = await LocalMeme.async_add(
            db=self.session,
            instance=LocalMeme(
                type=LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
                data=['some', 'some test', 'test something'],
                chat_id=message.message.chat.id,
            )
        )
        result = await BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        ).get_unknown_messages()
        self.assertListEqual(
            result,
            structs.DEFAULT_UNKNOWN_MESSAGE + local_memes.data
        )

    async def test_handle_free_words_empty(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'Some free word'
        result = await BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        ).handle_free_words()
        self.assertIsNone(result)

    async def test_handle_free_words_success(self):
        message = self.default_message.copy(deep=True)
        print(message.message.chat.id)
        message.message.text = 'Some_free_word'
        result = await BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        ).handle_free_words()
        self.assertEqual(
            result,
            'default answer'
        )

    async def test_handle_free_words_not_found(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'Some free word 1'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        result = await bread_service.handle_free_words()
        self.assertIsNone(result)
        bread_service.chat_id = 100500
        result = await bread_service.handle_free_words()
        self.assertIsNone(result)

    async def test_handle_free_words_value_is_dict(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'Some free word 3'
        result = await BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        ).handle_free_words()
        self.assertIsNone(result)

    async def test_handle_free_words_value_is_str(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'Some free word str'
        result = await BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        ).handle_free_words()
        self.assertEquals(
            result,
            'value',
        )

    async def test_handle_substring_words_as_list(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'I triggered my_substring in message'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertEqual(
            await bread_service.handle_substring_words(),
            'some_answer'
        )

    async def test_handle_substring_words_as_str(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'I triggered my_str in message'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertEqual(
            await bread_service.handle_substring_words(),
            'some_answer'
        )

    async def test_handle_substring_words_not_found(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'I triggered in message'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(await bread_service.handle_substring_words())
        bread_service.chat_id = 100500
        self.assertIsNone(await bread_service.handle_substring_words())

    async def test_handle_binds_is_not_command(self):
        message = self.default_message.copy(deep=True)
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(await bread_service.handle_binds())

    async def test_handle_binds_command_not_matched(self):
        message = self.default_message.copy(deep=True)
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        bread_service.command = 'wrong_bind_in_db'
        self.assertIsNone(await bread_service.handle_binds())

    async def test_handle_binds_success(self):
        message = self.default_message.copy(deep=True)
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        bread_service.command = 'test_command'
        self.assertEqual(
            bread_service.command,
            'test_command',
        )
        self.assertIn(
            'test_result',
            await bread_service.handle_binds(),
        )

    async def test_get_member_username(self):
        member = self.default_message.message.source.copy(deep=True)
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=self.default_message.message,
        )
        self.assertEqual(
            await bread_service.get_username(member=member),
            f'{member.first_name} {member.last_name}'
        )
        member.first_name = ''
        member.last_name = ''
        self.assertEqual(
            await bread_service.get_username(member=member),
            f'@{member.username}',
        )

    @respx.mock
    async def test_get_members(self):
        members = ChatMemberBodySchema(
            **{'result': [
                {'user': {'is_bot': False, 'user_name': 'uname1'}},
                {'user': {'is_bot': False, 'user_name': 'uname2'}},
                {'user': {'is_bot': False, 'user_name': 'uname3'}},
            ]}
        )
        content = members.dict()
        content['ok'] = True
        response = respx. \
            post('https://api.telegram.org/bot/getChatAdministrators'). \
            mock(return_value=Response(
            status_code=200,
            content=json.dumps(content)
        ))
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=self.default_message.message,
        )
        await bread_service.get_members()
        self.assertTrue(response.called)
        request = response.calls.last.request.read().decode(encoding='utf-8')
        self.assertEqual(
            json.loads(request),
            {'chat_id': self.default_message.message.chat.id}
        )
