import asyncio
import unittest

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from bread_bot.auth.models import User
from bread_bot.auth.schemas.auth import UserCreateSchema
from bread_bot.utils.dependencies import OffsetQueryParams
from bread_bot.utils.testing_tools import init_async_session


class AsyncDBTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = asyncio.run(init_async_session())
        cls.user_1 = User(
            username="some_user_1",
            email="some_user_1@mail.ru",
            hashed_password="12345",
        )
        cls.user_2 = User(
            username="some_user_2",
            email="some_user_2@mail.ru",
            hashed_password="12345",
        )

    async def asyncSetUp(self) -> None:
        self.default_user = await User.async_add(
            self.session,
            User(
                is_admin=False,
                username="default_user",
                email="default_user@mail.ru",
                hashed_password="12345",
            ),
        )

    async def asyncTearDown(self):
        await self.session.delete(self.default_user)
        await self.session.commit()
        await self.session.close()

    async def test_add_to_db(self):
        user = await User.async_add(self.session, self.user_1)
        self.assertEqual(
            user.username,
            "some_user_1",
        )
        self.assertEqual(user.email, "some_user_1@mail.ru")

    async def test_as_dict(self):
        self.assertEqual(
            self.default_user.as_dict(),
            {
                "created_at": self.default_user.created_at,
                "email": self.default_user.email,
                "first_name": None,
                "hashed_password": self.default_user.hashed_password,
                "id": self.default_user.id,
                "is_active": self.default_user.is_active,
                "surname": None,
                "updated_at": self.default_user.updated_at,
                "username": self.default_user.username,
                "is_admin": self.default_user.is_admin,
            },
        )

    async def test_create_by_schema(self):
        user_schema = UserCreateSchema(
            **{
                "email": "schema_user@mail.ru",
                "first_name": "first_name",
                "password": "password",
                "surname": None,
                "username": "schema_user",
            }
        )
        self.assertEqual(user_schema.username, "schema_user")
        self.assertEqual(user_schema.hashed_password, "password")
        user = await User.async_add_by_schema(self.session, user_schema)
        self.assertIsNotNone(user.id)
        self.assertEqual(
            user.username,
            user_schema.username,
        )

    async def test_rollbacks(self):
        user_object_1 = User(
            username="rollback_user",
            email="rollback_user@mail.ru",
            hashed_password="11112222",
        )
        user_object_2 = User(
            username="rollback_user",
            email="rollback_user@mail.ru",
            hashed_password="11112222",
        )
        user = await User.async_add(self.session, user_object_1)
        self.assertIsNotNone(user)
        with self.assertRaises(IntegrityError):
            await User.async_add(self.session, user_object_2)

        with self.assertRaises(IntegrityError):
            await User.async_add_all(
                self.session,
                [
                    user_object_2,
                ],
            )

    async def test_update_to_db(self):
        user = await User.async_add(self.session, self.user_2)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "some_user_2")
        self.assertEqual(user.email, "some_user_2@mail.ru")
        user.username = "some_user_3"
        user = await User.async_add(self.session, self.user_2)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "some_user_3")
        self.assertEqual(user.email, "some_user_2@mail.ru")

    async def test_bulk_create(self):
        users = list()
        for i in range(9):
            users.append(
                User(
                    username=f"bulk_user_{i}",
                    email=f"bulk_user_{i}@mail.ru",
                    hashed_password="11112222",
                )
            )
        result = await self.session.execute(select(User).where(User.username.in_([user.username for user in users])))
        before_count = len(result.scalars().all())
        await User.async_add_all(self.session, users)
        result = await self.session.execute(select(User).where(User.username.in_([user.username for user in users])))
        self.assertEqual(before_count + 9, len(result.scalars().all()))

    async def test_bulk_update(self):
        users = list()
        for i in range(9):
            users.append(
                User(
                    username=f"bulk_update_user_{i}",
                    email=f"bulk_update_user_{i}@mail.ru",
                    hashed_password="11112222",
                )
            )
        await User.async_add_all(self.session, users)
        updated_users = list()
        result = await self.session.stream(select(User).where(User.username.in_([user.username for user in users])))
        async for row in result:
            self.assertTrue(row[0].username.startswith("bulk_update_user"))
            row[0].username = row[0].username.replace("bulk_update_", "bulk_updated_")
            updated_users.append(row[0])
        await User.async_add_all(self.session, updated_users)
        result = await self.session.stream(
            select(User).where(User.username.in_([user.username for user in updated_users]))
        )
        async for row in result:
            self.assertTrue(row[0].username.startswith("bulk_updated_user"))

    async def test_filter(self):
        user1 = await User.async_add(
            self.session,
            User(
                username="test_simple_filter_1",
                email="test_simple_filter_1@mail.ru",
                hashed_password="test_simple_password_1",
            ),
        )
        user2 = await User.async_add(
            self.session,
            User(
                username="test_simple_filter_2",
                email="test_simple_filter_2@mail.ru",
                hashed_password="test_simple_password_2",
            ),
        )
        # CASE-1 Получение объекта через одно значение фильтром
        self.assertEqual(
            await User.async_filter(self.session, where=(User.username == user1.username), order_by=User.id), [user1]
        )
        self.assertEqual(
            await User.async_filter(self.session, where=(User.username == user2.username), order_by=User.id), [user2]
        )
        # CASE-2 Получение объекта через одно значение через first
        self.assertEqual(
            await User.async_first(self.session, where=(User.username == user1.username), order_by=User.id), user1
        )
        self.assertEqual(
            await User.async_first(self.session, where=(User.username == user2.username), order_by=User.id), user2
        )
        # CASE-3 Получение нескольких объектов по группировке id
        self.assertEqual(
            await User.async_filter(
                self.session,
                where=(
                    User.username.in_(
                        [
                            user1.username,
                            user2.username,
                        ]
                    )
                ),
                order_by=User.id,
            ),
            [user1, user2],
        )
        # CASE-4 Получение нескольких объектов
        # по группировке id в обратную сторону
        self.assertEqual(
            await User.async_filter(
                self.session,
                where=(
                    User.username.in_(
                        [
                            user1.username,
                            user2.username,
                        ]
                    )
                ),
                order_by=User.id.desc(),
            ),
            [user2, user1],
        )
        # CASE-5 Простое получение всех объектов таблицы
        self.assertIn(
            user1,
            await User.async_all(self.session),
        )
        self.assertIn(
            user2,
            await User.async_all(self.session),
        )
        # CASE-6 Тестирование получения объектов через offset и limit
        self.assertEqual(
            await User.async_offset_records(self.session, OffsetQueryParams(0, 1000)),
            await User.async_all(self.session),
        )
