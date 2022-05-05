import asyncio
import json
import unittest

import respx
from httpx import AsyncClient, Response

from bread_bot.telegramer.models import Member
from bread_bot.telegramer.clients.telegram_client import TelegramClient
from bread_bot.utils.testing_tools import test_app, \
    TEST_SERVER_URL, init_async_session


class GetMessageTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.telegram_client = TelegramClient()
        cls.test_request = {
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
        cls.test_request_json = json.dumps(cls.test_request)

    @respx.mock
    async def test_root_url(self):
        respx. \
            post('https://api.telegram.org/bot/sendMessage'). \
            mock(return_value=Response(
                status_code=200,
                content=json.dumps({'some_key': 'some_value'})
            ))
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post('/', data=self.test_request_json)
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            response.json(),
            'OK'
        )
        member: Member = await Member.async_first(
            db=self.session,
            where=Member.username == 'Lev_key'
        )
        self.assertEqual(
            member.username,
            'Lev_key'
        )
        self.assertEqual(
            member.first_name,
            'Lev'
        )
        self.assertEqual(
            member.last_name,
            'Kudryashov'
        )
        self.assertFalse(
            member.is_bot,
        )

    async def test_not_valid_body(self):
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post('/', data=json.dumps({'foo': 'bar'}))
        self.assertEqual(
            response.status_code,
            422
        )
        self.assertEqual(
            response.json(),
            {'detail': [{'loc': ['body', 'update_id'],
                         'msg': 'field required',
                         'type': 'value_error.missing'}]}
        )
