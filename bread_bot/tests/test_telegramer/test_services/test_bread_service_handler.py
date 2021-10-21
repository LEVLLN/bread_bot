import asyncio
import json
import unittest
from unittest import mock

from httpx import Response

from bread_bot.telegramer.models import LocalMeme, Chat, Property
from bread_bot.telegramer.schemas.telegram_messages import \
    StandardBodySchema, MemberSchema
from bread_bot.telegramer.services.bread_service_handler import \
    BreadServiceHandler
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, \
    PropertiesEnum
from bread_bot.utils.testing_tools import init_async_session


class BuildMessageTestCase(unittest.IsolatedAsyncioTestCase):
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

    async def test_undefined_message(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'undefined message'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertIsNone(result)

    async def test_call_unknown_command(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'Хлеб'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertIsNone(result)

    async def test_call_simple_command(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'Хлеб help'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'https://telegra.ph/HlebushekBot-10-04-3'
        )

    async def test_edited_message(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'edited message'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=True,
        )
        # Without properties
        result = await handler.build_message()
        self.assertIsNone(result)
        # Enable Chat flag
        chat = await Chat.async_first(
            db=self.session,
            where=Chat.chat_id == message.chat.id,
        )
        chat.is_edited_trigger = True
        await Chat.async_add(self.session, chat)
        result = await handler.build_message()
        self.assertIsNone(result)
        # With property
        await Property.async_add_by_kwargs(
            self.session,
            slug=PropertiesEnum.ANSWER_TO_EDIT.name,
            data=['answer to edit message']
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'answer to edit message',
        )

    async def test_triggers(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'some_free_word'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'default answer'
        )

    async def test_dirty_triggers(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'some_free_word additional word'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertIsNone(result)

    async def test_substrings(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'Some message with my_substring expression'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'some_answer'
        )

    async def test_local_bind(self):
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        # Command without trigger word
        message.text = 'test_command'
        result = await handler.build_message()
        self.assertIsNone(result)
        # Command with trigger word
        message.text = 'Хлеб test_command'
        result = await handler.build_message()
        self.assertIn(
            'test_result',
            result
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service_handler.BreadServiceHandler.get_members')
    async def test_who_is(self, get_members_mock: mock.Mock):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        get_members_mock.return_value = [test_member, ]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some param'
        # Test self chat
        result = await handler.who_is()
        self.assertIn(
            f'{message.source.first_name} {message.source.last_name}',
            result,
        )
        # Test group chat
        handler.chat_id = -111111
        result = await handler.who_is()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service.BreadService.get_members')
    async def test_have_is(self, get_members_mock: mock.Mock):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        get_members_mock.return_value = [test_member, ]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some param'
        # Test self chat
        result = await handler.who_have_is()
        self.assertIn(
            f'{message.source.first_name} {message.source.last_name}',
            result,
        )
        # Test group chat
        handler.chat_id = -111111
        result = await handler.who_have_is()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service.BreadService.get_members')
    async def test_gey_double(self, get_members_mock: mock.Mock):
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
        get_members_mock.return_value = [test_member, test_member_two]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_id = -111111
        result = await handler.gey_double()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )
        self.assertIn(
            f'{test_member_two.first_name} {test_member_two.last_name}',
            result,
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service.BreadService.get_members')
    async def test_top(self, get_members_mock: mock.Mock):
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
        get_members_mock.return_value = [test_member, test_member_two]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_id = -111111
        handler.params = 'Some param'
        result = await handler.top()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )
        self.assertIn(
            f'{test_member_two.first_name} {test_member_two.last_name}',
            result,
        )
        self.assertTrue(result.startswith('Топ'))
        self.assertIn(
            'Some param',
            result,
        )

    async def test_num(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.get_num()
        self.assertIsInstance(result, str)
        self.assertTrue(
            result.isnumeric()
        )

    async def test_get_chance(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some event'
        result = await handler.get_chance()
        self.assertTrue(
            result.startswith('Есть вероятность')
        )
        self.assertIn(
            handler.params,
            result,
        )

    async def test_choose_variant(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some event0, Some event1'
        result = await handler.choose_variant()
        self.assertIn(
            result,
            handler.params
        )
        self.assertNotEqual(
            len(result),
            len(handler.params),
        )

