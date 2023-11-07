import json
import unittest

import respx
from httpx import Response

from bread_bot.main.base_client import BaseHTTPClient


class BaseHTTPClientTestCase(unittest.IsolatedAsyncioTestCase):
    @respx.mock
    async def test_request(self):
        mock = respx.get("https://foo.bar/").mock(
            return_value=Response(status_code=200, content=json.dumps({"some_key": "some_value"}))
        )
        response = await BaseHTTPClient().request(url="https://foo.bar/", method="GET")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"some_key": "some_value"})
        assert mock.called

    @respx.mock
    async def test_request_exception(self):
        mock = respx.get("https://foo.bar/").mock(side_effect=ConnectionError("error"))
        response = await BaseHTTPClient().request(url="https://foo.bar/", method="GET")
        self.assertEqual(response.status_code, 0)
        self.assertEqual(
            response.content,
            b"",
        )
        assert mock.called
