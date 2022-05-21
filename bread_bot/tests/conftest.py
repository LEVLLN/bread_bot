import asyncio

import pytest
import uvloop

pytestmark = pytest.mark.asyncio
pytest_plugins = [
    "bread_bot.tests.fixtures",
    "bread_bot.tests.factory",
]


@pytest.fixture(scope='session', autouse=True)
def loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    return asyncio.new_event_loop()
