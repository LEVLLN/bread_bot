import asyncio
import unittest
from datetime import timedelta
from unittest import mock

from freezegun import freeze_time
from httpx import AsyncClient

from bread_bot.auth.methods.auth_methods import get_password_hash, \
    create_access_token
from bread_bot.auth.models import User
from bread_bot.utils.testing_tools import init_async_session, test_app, \
    TEST_SERVER_URL


class CreateTokenTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.data = {
            'username': 'create_token',
            'email': 'create_token@mail.ru',
            'hashed_password': get_password_hash('password'),
        }
        cls.user = asyncio.run(User.async_add(cls.session, User(**cls.data)))
        cls.expires_delta = timedelta(minutes=30)

    @freeze_time('00:00')
    async def test_get_token(self):
        token = await create_access_token(
            data={'sub': self.user.username},
            expires_delta=self.expires_delta,
        )
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post(
                '/token',
                data='username=create_token&password=password',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
        user = await User.async_first(
            self.session, User.username == 'create_token')
        self.assertIsNotNone(
            user
        )
        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertDictEqual(
            response.json(),
            {
                'access_token': token,
                'token_type': 'bearer'
            }
        )

    @freeze_time('00:00')
    async def test_get_token_user_not_found(self):
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post(
                '/token',
                data='username=wrong_user&password=password',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
        self.assertIsNotNone(
            await User.async_first(
                self.session, User.username == 'create_token')
        )
        self.assertEqual(
            response.status_code,
            401,
        )
        self.assertEqual(
            response.json(),
            {'detail': 'Incorrect username or password'}
        )

    @freeze_time('00:00')
    @mock.patch('bread_bot.auth.routes.auth.authenticate_user')
    async def test_get_token_user_error(self, mock_method: mock.Mock):
        mock_method.side_effect = Exception('some error')
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post(
                '/token',
                content='username=create_token&password=password',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
        user = await User.async_first(
            self.session, User.username == 'create_token')
        mock_method.assert_called_once()
        self.assertIsNotNone(
            user
        )
        self.assertEqual(
            response.status_code,
            500,
        )
        self.assertEqual(
            response.content.decode(),
            'Internal Server Error',
        )

    @freeze_time('00:00')
    @mock.patch('bread_bot.auth.routes.auth.authenticate_user')
    async def test_get_token_user_none(self, mock_method: mock.Mock):
        mock_method.return_value = None
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post(
                '/token',
                content='username=create_token&password=password',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
        mock_method.assert_called_once()
        self.assertEqual(
            response.status_code,
            401,
        )
        self.assertEqual(
            response.json(),
            {'detail': 'Incorrect username or password'}
        )
