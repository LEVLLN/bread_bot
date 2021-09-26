import asyncio
import json
import unittest
from unittest import mock
from unittest.mock import Mock

from httpx import AsyncClient

from bread_bot.auth.models import User
from bread_bot.auth.schemas.auth import UserCreateSchema, UserInfoSchema
from bread_bot.utils.testing_tools import init_async_session, test_app, \
    TEST_SERVER_URL


class CreateUserTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.data = {
            'username': 'test_create',
            'email': 'test_create@mail.ru',
            'password': 'password',
        }
        cls.schema = UserCreateSchema(
            **cls.data
        )

    async def test_create_user(self):
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post('/users/create',
                                     data=json.dumps(self.data))
        user = await User.async_first(
            self.session, User.username == 'test_create')
        self.assertIsNotNone(
            user
        )
        user_schema = UserInfoSchema.from_orm(user)
        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertDictEqual(
            response.json(),
            dict(user_schema)
        )

    @mock.patch('bread_bot.auth.models.users.User.async_add_by_schema')
    async def test_create_user_error(self, mock_add_schema: Mock):
        mock_add_schema.side_effect = Exception('some_exception')
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.post('/users/create',
                                     content=json.dumps(self.data))
        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            response.json(),
            {'detail': 'Ошибка регистрации пользователя'}
        )
