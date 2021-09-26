import asyncio
import unittest

from httpx import AsyncClient

from bread_bot.auth.methods.auth_methods import get_password_hash, \
    create_access_token
from bread_bot.auth.models import User
from bread_bot.auth.schemas.auth import UserInfoSchema
from bread_bot.utils.testing_tools import init_async_session, test_app, \
    TEST_SERVER_URL


class GetUsersTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.data = {
            'username': 'test_get_user',
            'email': 'test_get_user@mail.ru',
            'hashed_password': get_password_hash('password'),
        }
        cls.user = asyncio.run(User.async_add(cls.session, User(**cls.data)))

    async def test_get_users(self):
        token = await create_access_token(data={'sub': self.user.username})
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.get(
                '/users',
                headers={
                    'Authorization': f'Bearer {token}'
                })
        user = await User.async_first(
            self.session, User.username == 'test_get_user')
        self.assertIsNotNone(
            user
        )
        user_schema = UserInfoSchema.from_orm(user)
        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertListEqual(
            response.json(),
            [user_schema, ]
        )

    async def test_public_users(self):
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            await User.async_add(db=self.session, instance=self.user)
            response = await ac.get('/users/public/')

        self.assertListEqual(
            response.json(),
            [
                {
                    'email': 'test_get_user@mail.ru',
                    'id': 1,
                    'surname': None,
                    'username': 'test_get_user',
                    'is_active': True,
                    'first_name': None
                }
            ]
        )
