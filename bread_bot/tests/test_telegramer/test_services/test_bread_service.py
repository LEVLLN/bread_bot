import asyncio
import json
import unittest
from unittest import mock

import respx
from httpx import Response
from sqlalchemy import and_

from bread_bot.telegramer.models import Member, \
    LocalMeme, Chat, ChatToMember, Stats
from bread_bot.telegramer.schemas.telegram_messages import \
    StandardBodySchema, \
    ChatMemberBodySchema, MemberSchema, MessageSchema
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
        asyncio.run(LocalMeme.async_add_by_kwargs(
            db=cls.session,
            type=LocalMemeTypesEnum.FREE_WORDS.name,
            data={
                'some free word str': 'value',
                'some_free_word': ['default answer'],
                'some free word 3': {'default answer': 'value'},
                'some free word 2': ['default answer']
            },
            chat_id=cls.default_message.message.chat.id,
        ))
        asyncio.run(
            LocalMeme.async_add_by_kwargs(
                db=cls.session,
                type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
                data={
                    'my_substring': ['some_answer'],
                    'my_str': 'some_answer',
                    'ch': 'two_char_answer',
                },
                chat_id=cls.default_message.message.chat.id,
            )
        )

        asyncio.run(
            LocalMeme.async_add_by_kwargs(
                db=cls.session,
                type=LocalMemeTypesEnum.MEME_NAMES.name,
                chat_id=cls.default_message.message.chat.id,
                data={
                    'test_command': ['test_result'],
                }
            )

        )

    async def test_handle_chat_create(self):
        message = self.default_message.copy(deep=True)
        message.message.chat.title = 'Some Chat'
        message.message.chat.id = 12345

        self.assertIsNone(
            await Chat.async_first(
                db=self.session,
                where=Chat.chat_id == message.message.chat.id)
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
                where=Chat.chat_id == message.message.chat.id
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
                where=Chat.chat_id == message.message.chat.id)
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
                where=Chat.chat_id == message.message.chat.id
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
                where=filter_param
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
                where=filter_param
            ),
            member
        )

    async def test_handle_member_update(self):
        message = self.default_message.copy(deep=True)
        message.message.source.username = 'test_user'
        member = await Member.async_add_by_kwargs(
            db=self.session,
            username=message.message.source.username,
        )
        filter_param = Member.username == message.message.source.username
        self.assertIsNotNone(
            await Member.async_first(
                db=self.session,
                where=filter_param)
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
                where=filter_param
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
        result = await bread_service.parse_incoming_message()
        self.assertIsNone(result)
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
        member = await Member.async_add_by_kwargs(
            self.session, username='Binder')
        chat = await Chat.async_add_by_kwargs(
            self.session, name='BinderGroup', chat_id=20000)
        await bread_service.handle_chats_to_members(member.id, chat.id)
        chat_to_members = await ChatToMember.async_filter(
            db=self.session,
            where=and_(
                ChatToMember.chat_id == chat.id,
                ChatToMember.member_id == member.id,
            )
        )
        self.assertIsNotNone(chat_to_members)
        self.assertEqual(len(chat_to_members), 1)
        second_member = await Member.async_add_by_kwargs(
            self.session, username='Binder2')
        await bread_service.handle_chats_to_members(second_member.id, chat.id)
        chat_to_members = await ChatToMember.async_filter(
            db=self.session,
            where=and_(
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
            where=and_(
                ChatToMember.chat_id == 100500,
                ChatToMember.member_id == 100500,
            )
        )
        self.assertListEqual(chat_to_members, [])
        self.assertEqual(len(chat_to_members), 0)

    async def test_count_stats(self):
        member = await Member.async_add_by_kwargs(
            self.session,
            username='Statistic')
        chat = await Chat.async_add_by_kwargs(
            self.session,
            name='StatisticGroup',
            chat_id=20001)
        message = self.default_message.copy(deep=True)
        message.message.source.username = member.username
        message.message.chat.id = chat.chat_id
        self.assertIsNone(
            await Stats.async_first(
                db=self.session,
                where=and_(
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
            where=and_(
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
        result = await bread_service.get_list_messages()
        self.assertListEqual(
            result,
            structs.DEFAULT_UNKNOWN_MESSAGE,
        )
        local_memes = await LocalMeme.async_add_by_kwargs(
            db=self.session,
            type=LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
            data=['some', 'some test', 'test something'],
            chat_id=message.message.chat.id,
        )
        result = await BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        ).get_list_messages()
        self.assertListEqual(
            result,
            structs.DEFAULT_UNKNOWN_MESSAGE + local_memes.data
        )

    async def test_handle_rude_words(self):
        message = self.default_message.message.copy(deep=True)
        message.chat.id = 12122221
        # Message without reply
        handler = BreadService(
            client=self.telegram_client,
            message=message,
            db=self.session,
        )
        handler.chat_id = message.chat.id
        # Without LOCAL_MEME
        result = await handler.handle_rude_words()
        self.assertIn(
            result,
            structs.DEFAULT_UNKNOWN_MESSAGE
        )
        # With LOCAL_MEME, Without REPLY
        await LocalMeme.async_add_by_kwargs(
            db=self.session,
            chat_id=handler.chat_id,
            type=LocalMemeTypesEnum.RUDE_WORDS.name,
            data=['some_rude_word', 'some_rude_word']
        )
        result = await handler.handle_rude_words()
        self.assertEqual(
            result,
            'some_rude_word'
        )
        # With LOCAL_MEME, With REPLY
        message.reply = MessageSchema(
            message_id=11110,
            chat=message.chat,
            source=message.source,
            text='Foo',
        )
        handler = BreadService(
            client=self.telegram_client,
            message=message,
            db=self.session,
        )
        result = await handler.handle_rude_words()
        self.assertEqual(
            result,
            f'@{message.source.username}\nsome_rude_word'
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

    async def test_handle_substring_words_dirty(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'I triggered amy_substrings in message'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertEqual(
            await bread_service.handle_substring_words(),
            'some_answer'
        )

    async def test_handle_substring_words_two_char_answer(self):
        message = self.default_message.copy(deep=True)
        message.message.text = 'I triggered ch in message'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        self.assertIsNone(
            await bread_service.handle_substring_words(),
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
        self.assertIsNone(await bread_service.handle_bind_words())

    async def test_handle_binds_command_not_matched(self):
        message = self.default_message.copy(deep=True)
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message.message,
        )
        bread_service.command = 'wrong_bind_in_db'
        self.assertIsNone(await bread_service.handle_bind_words())

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
            await bread_service.handle_bind_words(),
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

    async def test_add_local_meme(self):
        message = self.default_message.message.copy(deep=True)
        message.chat.id = 12321123
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message,
        )
        bread_service.params = 'param=value1'
        # Create
        local_meme = await LocalMeme.get_local_meme(
            db=self.session,
            chat_id=message.chat.id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )
        self.assertIsNone(local_meme)
        result = await bread_service.add_local_meme(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name
        )
        self.assertEqual(
            result,
            'Ура! У группы появились Привязки'
        )
        local_meme = await LocalMeme.get_local_meme(
            db=self.session,
            chat_id=message.chat.id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )
        self.assertIsNotNone(local_meme)
        self.assertEqual(
            local_meme.data,
            {'param': ['value1']}
        )
        # Add new value
        bread_service.params = 'param=value2'
        result = await bread_service.add_local_meme(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name
        )
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.get_local_meme(
            db=self.session,
            chat_id=message.chat.id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )
        self.assertEqual(
            local_meme.data,
            {'param': ['value1', 'value2']}
        )
        # Add new key
        bread_service.params = 'param1=value1'
        result = await bread_service.add_local_meme(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name
        )
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.get_local_meme(
            db=self.session,
            chat_id=message.chat.id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )
        self.assertEqual(
            local_meme.data,
            {'param': ['value1', 'value2'], 'param1': ['value1']}
        )

    async def test_delete_local_meme(self):
        message = self.default_message.message.copy(deep=True)
        message.chat.id = 12321122
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message,
        )
        bread_service.params = 'param4'
        # Chat does not has local_memes
        result = await bread_service.delete_local_meme(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)
        self.assertEqual(
            result,
            'У чата отсутствуют Триггеры'
        )
        await LocalMeme.async_add_by_kwargs(
            db=self.session,
            type=LocalMemeTypesEnum.FREE_WORDS.name,
            data={
                'param1': ['value1'],
                'param2': ['value2'],
                'param3': ['value3'],
            },
            chat_id=message.chat.id,
        )
        # Delete not existed key
        result = await bread_service.delete_local_meme(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)
        local_meme = await LocalMeme.get_local_meme(
            db=self.session,
            chat_id=message.chat.id,
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        self.assertEqual(
            result,
            'У чата отсутствуют Триггеры'
        )
        self.assertEqual(
            len(local_meme.data.keys()),
            3
        )
        # Delete
        bread_service.params = 'param3'
        result = await bread_service.delete_local_meme(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)
        local_meme = await LocalMeme.get_local_meme(
            db=self.session,
            chat_id=message.chat.id,
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        self.assertEqual(
            result,
            'Сделал'
        )
        self.assertDictEqual(
            local_meme.data,
            {'param1': ['value1'], 'param2': ['value2']}
        )

    async def test_show_local_memes(self):
        message = self.default_message.message.copy(deep=True)
        message.chat.id = 12321121
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message,
        )
        # local_memes does not exists
        bread_service.params = 'param1'
        result = await bread_service.show_local_memes(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        self.assertEqual(
            result,
            'У группы отсутствуют Триггеры'
        )
        local_meme = await LocalMeme.async_add_by_kwargs(
            db=self.session,
            type=LocalMemeTypesEnum.FREE_WORDS.name,
            data={},
            chat_id=message.chat.id,
        )
        # local_meme does not have data
        result = await bread_service.show_local_memes(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        self.assertEqual(
            local_meme.data,
            {}
        )
        self.assertEqual(
            result,
            'У группы отсутствуют Триггеры'
        )
        # show local_memes
        local_meme.data = {
            'param1': ['value1'],
            'param2': ['value2'],
            'param3': ['value3'],
        }
        local_meme = await LocalMeme.async_add(
            db=self.session,
            instance=local_meme
        )
        result = await bread_service.show_local_memes(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        self.assertDictEqual(
            local_meme.data,
            {
                'param1': ['value1'],
                'param2': ['value2'],
                'param3': ['value3'],
            }
        )
        self.assertEqual(
            result,
            '\n'.join(['param1', 'param2', 'param3'])
        )

    async def test_add_list_value(self):
        message = self.default_message.message.copy(deep=True)
        message.chat.id = 12321120
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message,
        )
        # Create local_meme object
        bread_service.params = 'value1'
        result = await bread_service.add_list_value(
            LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )
        result_name = LocalMemeTypesEnum[
            str(LocalMemeTypesEnum.UNKNOWN_MESSAGE.name)]
        local_meme = await LocalMeme.get_local_meme(
            db=self.session,
            chat_id=message.chat.id,
            meme_type=LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )
        self.assertEqual(
            result,
            f'Ура! У группы появились {result_name.value}'
        )
        self.assertEqual(
            len(local_meme.data),
            1
        )
        self.assertIsInstance(local_meme.data, list)
        # Add new value
        bread_service.params = 'value2'
        result = await bread_service.add_list_value(
            LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )

        self.assertEqual(
            len(local_meme.data),
            2
        )
        self.assertListEqual(
            local_meme.data,
            ['value1', 'value2']
        )
        self.assertEqual(
            result,
            'Сделал'
        )
        # Add already existed value
        bread_service.params = 'value2'
        result = await bread_service.add_list_value(
            LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )
        self.assertEqual(
            len(local_meme.data),
            2
        )
        self.assertListEqual(
            local_meme.data,
            ['value1', 'value2']
        )
        self.assertEqual(
            result,
            'Сделал'
        )

    async def test_show_stats(self):
        message = self.default_message.message.copy(deep=True)
        message.chat.id = 12321155
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message,
        )
        # Stats does not exists
        result = await bread_service.show_stats()
        self.assertEqual(
            result,
            'Пока не набрал статистики'
        )
        # Show stats
        member = await bread_service.handle_member(member=message.source)
        chat = await bread_service.handle_chat()
        await bread_service.handle_chats_to_members(member.id, chat.id)
        stats = []
        for stat_name in [StatsEnum.QUOTER.name,
                          StatsEnum.TOTAL_CALL_SLUG.name]:
            stats.append(
                Stats(
                    member_id=member.id,
                    chat_id=chat.chat_id,
                    slug=stat_name,
                    count=1,
                )
            )
        await Stats.async_add_all(
            db=self.session,
            instances=stats,
        )
        result = await bread_service.show_stats()
        self.assertEqual(
            result,
            'Сколько раз просил цитату:\n'
            'Tester Testerov - 1\n\n\nСколько раз вызвал бота:\n'
            'Tester Testerov - 1\n\n\n'
        )
        # Sorting with other members in same stats slug
        new_member = message.source.copy(deep=True)
        new_member.id = 4040
        new_member.username = 'clicker'
        new_member.first_name = 'Click'
        new_member.last_name = 'Clickovich'
        member = await bread_service.handle_member(member=new_member)
        await Stats.async_add_by_kwargs(
            db=self.session,
            member_id=member.id,
            chat_id=chat.chat_id,
            slug=StatsEnum.QUOTER.name,
            count=9,
        )
        result = await bread_service.show_stats()
        self.assertEqual(
            result,
            'Сколько раз просил цитату:\n'
            'Click Clickovich - 9\nTester Testerov - 1\n\n\n'
            'Сколько раз вызвал бота:\n'
            'Tester Testerov - 1\n\n\n'
        )

    async def test_propagate_members_memes(self):
        message = self.default_message.message.copy(deep=True)
        source_chat = await Chat.async_add_by_kwargs(
            db=self.session,
            chat_id=5555,
            name='SourceChat'
        )
        member_schema = message.source
        member_schema.id = 5555
        member_schema.first_name = 'Source Name'
        member_schema.last_name = 'LastName'
        member = await Member.async_add_by_kwargs(
            db=self.session,
            username=member_schema.username,
            first_name=member_schema.first_name,
            last_name=member_schema.last_name,
            member_id=member_schema.id,
        )
        message.chat.id = source_chat.id
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message,
        )
        bread_service.params = 'DestinationChat'
        # Without destination chat in DB
        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Не найдено чата для отправки'
        )
        # Member to member sending
        destination_chat = await Chat.async_add_by_kwargs(
            db=self.session,
            chat_id=6666,
            name='DestinationChat'
        )
        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Невозможно копировать другим людям свои данные'
        )
        # Member to group without permission to chat
        destination_chat.chat_id = -6666
        destination_chat = await Chat.async_add(
            db=self.session,
            instance=destination_chat,
        )
        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Нет прав на указанный чат'
        )
        # Source chat is not a member
        bread_service.chat_id = -5555
        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Нельзя из чата копировать в другой чат. '
            'Только из личных сообщений с ботом!'
        )
        # member not exists
        bread_service.chat_id = 5555
        member.username = 'ChangedUsername'
        await Member.async_add(
            db=self.session,
            instance=member,
        )
        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Что-то пошло не так'
        )
        # LocalMemes not found
        member.username = 'Source Name'
        member = await Member.async_add(
            db=self.session,
            instance=member,
        )
        message.source.username = 'Source Name'
        bread_service = BreadService(
            client=self.telegram_client,
            db=self.session,
            message=message,
        )
        bread_service.params = 'DestinationChat'
        await bread_service.handle_chats_to_members(
            member_id=member.id,
            chat_id=destination_chat.id,
        )
        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Не найдено данных для копирования'
        )
        # Create key
        source_local_meme = await LocalMeme.async_add_by_kwargs(
            self.session,
            chat_id=bread_service.chat_id,
            type=LocalMemeTypesEnum.MEME_NAMES.name,
            data={
                'param1': ['value1']
            }
        )
        destination_local_meme = await LocalMeme.async_add_by_kwargs(
            self.session,
            chat_id=destination_chat.chat_id,
            type=LocalMemeTypesEnum.MEME_NAMES.name,
            data={}
        )

        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Сделал'
        )
        await self.session.refresh(destination_local_meme)
        self.assertEqual(
            destination_local_meme.data,
            {'param1': ['value1']}
        )
        # Add value to same key
        data = {'param1': ['value1', 'value2']}
        source_local_meme.data = data
        await LocalMeme.async_add(
            db=self.session,
            instance=source_local_meme,
        )
        result = await bread_service.propagate_members_memes()
        self.assertEqual(
            result,
            'Сделал'
        )
        self.assertEqual(
            len(destination_local_meme.data['param1']),
            2
        )
        self.assertSetEqual(
            set(destination_local_meme.data['param1']),
            {'value1', 'value2'}
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service.BreadService.get_members')
    async def test_get_one_of_group(self, get_members_mock: mock.Mock):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        get_members_mock.return_value = [test_member, ]
        message = self.default_message.message.copy(deep=True)
        handler = BreadService(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some param'
        # Test self chat
        result = await handler.get_one_of_group()
        self.assertIn(
            f'{message.source.first_name} {message.source.last_name}',
            result,
        )
        # Test group chat
        handler.chat_id = -111111
        result = await handler.get_one_of_group()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )
