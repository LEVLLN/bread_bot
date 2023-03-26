import unittest

from httpx import AsyncClient

from bread_bot.utils.testing_tools import TEST_SERVER_URL, test_app


class RootRouteTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_root_url(self):
        async with AsyncClient(app=test_app, base_url=TEST_SERVER_URL) as ac:
            response = await ac.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"foo": "baz"})
