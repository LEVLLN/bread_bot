import asyncio
import json
import unittest
from unittest import mock

import respx
from httpx import Response

from bread_bot.telegramer.schemas.telegram_messages import StandardBodySchema
from bread_bot.telegramer.services.message_handler import MessageHandler
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.utils import structs
from bread_bot.utils.testing_tools import init_async_session


class MessageHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.telegram_client = TelegramClient()
        cls.default_return_value = Response(
            status_code=200,
            content=json.dumps({'some_key': 'some_value'})
        )
        cls.test_data = {
            'update_id': 123,
            'message': {
                'message_id': 1,
                'from': {
                    'id': 123,
                    'is_bot': False,
                    'first_name': 'Lev',
                    'last_name': 'Kudryashov',
                    'username': 'Lev_key',
                    'language_code': 'en'
                },
                'chat': {
                    'id': 123,
                    'first_name': 'Lev',
                    'last_name': 'Kudryashov',
                    'username': 'Lev_key',
                    'type': 'private'
                },
                'date': 12343,
                'text': 'Хлеб'
            }
        }
        cls.test_edited_data = {
            'update_id': 123,
            'edited_message': {
                'message_id': 1,
                'from': {
                    'id': 123,
                    'is_bot': False,
                    'first_name': 'Lev',
                    'last_name': 'Kudryashov',
                    'username': 'Lev_key',
                    'language_code': 'en'
                },
                'chat': {
                    'id': 123,
                    'first_name': 'Lev',
                    'last_name': 'Kudryashov',
                    'username': 'Lev_key',
                    'type': 'private'
                },
                'date': 12343,
                'text': 'Хлеб'
            }
        }
        cls.test_message = StandardBodySchema(**cls.test_data)
        cls.test_edited_message = StandardBodySchema(**cls.test_edited_data)

    async def test_validate_message(self):
        mh = MessageHandler(
            request_body=self.test_message,
            db=self.session
        )
        self.assertTrue(
            mh.has_message
        )
        self.assertFalse(
            mh.has_edited_message
        )
        self.assertEqual(
            mh.message,
            self.test_message.message,
        )
        self.assertTrue(await mh.validate_command())

    async def test_validate_edited_message(self):
        mh = MessageHandler(
            request_body=self.test_edited_message,
            db=self.session
        )
        self.assertFalse(
            mh.has_message
        )
        self.assertTrue(
            mh.has_edited_message
        )
        self.assertEqual(
            mh.message,
            self.test_edited_message.edited_message,
        )
        self.assertTrue(await mh.validate_command())

    async def test_invalid_message(self):
        mh = MessageHandler(
            request_body=StandardBodySchema(**{
                'update_id': 123,
            })
        )
        self.assertIsNone(mh.message)
        self.assertFalse(mh.has_message)
        self.assertFalse(mh.has_edited_message)
        self.assertFalse(await mh.validate_command())

    @respx.mock
    @mock.patch('bread_bot.telegramer.services.message_handler.'
                'BreadServiceHandler.build_message')
    async def test_success_handle_message(self, build_message_mock: mock.Mock):
        build_message_mock.return_value = 'Some text'
        response = respx. \
            post('https://api.telegram.org/bot/sendMessage'). \
            mock(return_value=self.default_return_value)
        mh = MessageHandler(
            request_body=self.test_message,
            db=self.session
        )
        await mh.handle_message()
        request_data = json.loads(
            response.calls.last.request.read().decode(encoding='utf-8'))
        self.assertEqual(
            request_data['text'],
            'Some text'
        )
        self.assertEqual(
            request_data['chat_id'],
            self.test_message.message.chat.id,
        )
        self.assertTrue(response.called)
        build_message_mock.assert_called_once()

    @respx.mock
    @mock.patch('bread_bot.telegramer.services.message_handler.'
                'BreadServiceHandler.build_message')
    async def test_success_handle_message_empty(
            self,
            build_message_mock: mock.Mock
    ):
        build_message_mock.return_value = None
        response = respx. \
            post('https://api.telegram.org/bot/sendMessage'). \
            mock(return_value=self.default_return_value)
        mh = MessageHandler(
            request_body=self.test_message,
            db=self.session
        )
        await mh.handle_message()
        self.assertFalse(response.called)
        build_message_mock.assert_called()

    @respx.mock
    @mock.patch('bread_bot.telegramer.services.message_handler.'
                'BreadServiceHandler.build_message')
    async def test_handle_message_error(
            self,
            build_message_mock: mock.Mock
    ):
        build_message_mock.side_effect = Exception
        response = respx. \
            post('https://api.telegram.org/bot/sendMessage'). \
            mock(return_value=self.default_return_value)
        mh = MessageHandler(
            request_body=self.test_message,
            db=self.session
        )
        with self.assertRaises(Exception):
            await mh.handle_message()
        request_data = json.loads(
            response.calls.last.request.read().decode(encoding='utf-8'))
        self.assertIn(
            request_data['text'],
            structs.ERROR_CHAT_MESSAGES
        )
        self.assertEqual(
            request_data['chat_id'],
            self.test_message.message.chat.id,
        )
        self.assertTrue(response.called)
        build_message_mock.assert_called()
