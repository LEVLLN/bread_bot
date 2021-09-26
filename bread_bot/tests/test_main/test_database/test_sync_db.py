import unittest

from sqlalchemy.exc import IntegrityError

from bread_bot.auth.models import User
from bread_bot.auth.schemas.auth import UserCreateSchema
from bread_bot.utils.testing_tools import init_sync_session


class SyncDBTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = init_sync_session()
        cls.user_1 = User(
            username='some_user_1',
            email='some_user_1@mail.ru',
            hashed_password='12345',
        )
        cls.user_2 = User(
            username='some_user_2',
            email='some_user_2@mail.ru',
            hashed_password='12345',
        )

    async def test_add_to_db(self):
        user = User.sync_add(self.session, self.user_1)
        self.assertIsNotNone(user)
        self.assertEqual(
            user.username,
            'some_user_1'
        )
        self.assertEqual(
            user.email,
            'some_user_1@mail.ru'
        )

    async def test_update_to_db(self):
        user = User.sync_add(self.session, self.user_2)
        self.assertIsNotNone(user)
        self.assertEqual(
            user.username,
            'some_user_2'
        )
        self.assertEqual(
            user.email,
            'some_user_2@mail.ru'
        )
        user.username = 'some_user_3'
        user = User.sync_add(self.session, self.user_2)
        self.assertIsNotNone(user)
        self.assertEqual(
            user.username,
            'some_user_3'
        )
        self.assertEqual(
            user.email,
            'some_user_2@mail.ru'
        )

    async def test_rollbacks(self):
        user1 = User(
            username='rollback_user',
            email='rollback_user@mail.ru',
            hashed_password='password'
        )
        user2 = User(
            username='rollback_user',
            email='rollback_user@mail.ru',
            hashed_password='password'
        )
        User.sync_add(self.session, user1)
        with self.assertRaises(IntegrityError):
            User.sync_add(self.session, user2)

    async def test_add_by_schema(self):
        user_schema = UserCreateSchema(
            **{
                'email': 'schema_user@mail.ru',
                'first_name': 'first_name',
                'password': 'password',
                'surname': None,
                'username': 'schema_user',
            }
        )
        self.assertEqual(
            user_schema.username,
            'schema_user'
        )
        self.assertEqual(
            user_schema.hashed_password,
            'password'
        )
        user = User.sync_add_by_schema(self.session, user_schema)
        self.assertIsNotNone(user.id)
        self.assertEqual(
            user.username,
            user_schema.username,
        )

    async def test_first(self):
        user = User.sync_add(
            self.session,
            User(
                username='first_user',
                email='first_user@mail.ru',
                hashed_password='12345',
            )
        )
        self.assertIsNotNone(
            User.first(self.session, username=user.username),
        )
