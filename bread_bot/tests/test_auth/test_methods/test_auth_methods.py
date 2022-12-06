import asyncio
import datetime
import unittest

from fastapi import HTTPException
from freezegun import freeze_time
from jose import jwt

from bread_bot.auth.methods.auth_methods import (
    get_password_hash,
    verify_password,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
)
from bread_bot.auth.models import User
from bread_bot.main.settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from bread_bot.utils.testing_tools import init_async_session


class AuthMethodsTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.user = User.sync_add(
            cls.session, User(username="test", email="test@mail.ru", hashed_password=get_password_hash("password"))
        )
        cls.access_token_expires_delta = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    async def test_verify_password(self):
        self.assertTrue(
            verify_password(
                "password",
                self.user.hashed_password,
            )
        )

    async def test_authenticate_user(self):
        self.assertEqual(
            await authenticate_user(self.session, self.user.username, "password"),
            self.user,
        )

    async def test_authenticate_user_not_found(self):
        self.assertIsNone(
            await authenticate_user(self.session, "wrong_username", "password"),
        )

    async def test_authenticate_user_wrong_password(self):
        self.assertIsNone(
            await authenticate_user(self.session, self.user.username, "wrong"),
        )

    @freeze_time("00:00")
    async def test_create_access_token(self):
        access_token = await create_access_token(
            data={"sub": self.user.username}, expires_delta=self.access_token_expires_delta
        )
        exp = datetime.datetime.now() + self.access_token_expires_delta
        self.assertIsNotNone(access_token)
        self.assertEqual(
            access_token,
            jwt.encode(
                {
                    "sub": self.user.username,
                    "exp": exp,
                },
                key=SECRET_KEY,
                algorithm=ALGORITHM,
            ),
        )

    @freeze_time("00:00")
    async def test_create_access_token_without_delta(self):
        access_token = await create_access_token(
            data={"sub": self.user.username},
        )
        exp = datetime.datetime.now() + datetime.timedelta(minutes=15)
        self.assertIsNotNone(access_token)
        self.assertEqual(
            access_token,
            jwt.encode(
                {
                    "sub": self.user.username,
                    "exp": exp,
                },
                key=SECRET_KEY,
                algorithm=ALGORITHM,
            ),
        )

    async def test_get_current_user(self):
        token = await create_access_token(
            data={"sub": self.user.username}, expires_delta=self.access_token_expires_delta
        )
        result_user = await get_current_user(self.session, token)
        self.assertEqual(
            self.user,
            result_user,
        )

    async def test_get_current_user_is_none(self):
        token = await create_access_token(data={"sub": None}, expires_delta=self.access_token_expires_delta)
        with self.assertRaises(HTTPException):
            await get_current_user(self.session, token)

    async def test_get_current_user_wrong(self):
        token = await create_access_token(data={"sub": "wrong"}, expires_delta=self.access_token_expires_delta)
        with self.assertRaises(HTTPException):
            await get_current_user(self.session, token)

    async def test_get_current_active_user(self):
        self.assertTrue(await get_current_active_user(current_user=self.user))

    async def test_get_current_active_user_inactive(self):
        self.user.is_active = False
        User.sync_add(self.session, self.user)
        with self.assertRaises(HTTPException):
            await get_current_active_user(current_user=self.user)
