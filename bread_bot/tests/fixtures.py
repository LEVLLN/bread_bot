import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from bread_bot.main.database.base import DeclarativeBase
from bread_bot.telegramer.schemas.telegram_messages import StandardBodySchema
from bread_bot.telegramer.services.message_service import MessageService


@pytest.fixture
async def db():
    # Асинхронные механизмы БД
    test_async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:?check_same_thread=False",
    )
    TestAsyncSessionLocal = sessionmaker(
        test_async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with test_async_engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)
    session = TestAsyncSessionLocal()
    yield session
    await session.rollback()


@pytest.fixture
def request_body_message():
    return StandardBodySchema(
        **{
            "update_id": 123,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 134,
                    "is_bot": False,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "language_code": "ru"
                },
                "chat": {
                    "id": 134,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "type": "private"
                },
                "date": 12343,
                "text": "Test"
            }
        }
    )


@pytest.fixture
def reply_voice():
    return StandardBodySchema(
        **{
            "update_id": 958678863,
            "message": {
                "message_id": 13900,
                "from": {
                    "id": 296382623,
                    "is_bot": False,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "language_code": "en"
                },
                "chat": {
                    "id": 296382623,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "type": "private"
                },
                "date": 1655506631,
                "reply_to_message": {
                    "message_id": 13898,
                    "from": {
                        "id": 296382623,
                        "is_bot": False,
                        "first_name": "Tester",
                        "last_name": "Testerov",
                        "username": "Test_test",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 296382623,
                        "first_name": "Tester",
                        "last_name": "Testerov",
                        "username": "Test_test",
                        "type": "private"
                    },
                    "date": 1655506619,
                    "voice": {
                        "duration": 3,
                        "mime_type": "audio/ogg",
                        "file_id": "AwACAgIAAxkBAAI2SmKtBrufIcWi95pc7qz3NkFNPnZNAAI5HwACp3ZpSdqwY0ZTyPojJAQ",
                        "file_unique_id": "AgADOR8AAqd2aUk",
                        "file_size": 11599
                    }
                },
                "text": "1234567"
            }
        }
    )


@pytest.fixture
def reply_photo():
    return StandardBodySchema(
        **{
            "update_id": 958678863,
            "message": {
                "message_id": 13900,
                "from": {
                    "id": 296382623,
                    "is_bot": False,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "language_code": "en"
                },
                "chat": {
                    "id": 296382623,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "type": "private"
                },
                "date": 1655506631,
                "reply_to_message": {
                    "message_id": 13951,
                    "from": {
                        "id": 296382623,
                        "is_bot": False,
                        "first_name": "Tester",
                        "last_name": "Testerov",
                        "username": "Test_test",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 296382623,
                        "first_name": "Tester",
                        "last_name": "Testerov",
                        "username": "Test_test",
                        "type": "private"
                    },
                    "date": 1655570499,
                    "photo": [
                        {
                            "file_id": "IAAxkBAAI2f2KuAAFDf8weZSPvhJfqXj_NHirgAwACUb0xG6d2cUn78sce7lCKywEAAwIAA3MAAyQE",
                            "file_unique_id": "AQADUb0xG6d2cUl4",
                            "file_size": 1433,
                            "width": 69,
                            "height": 90},
                        {
                            "file_id": "IAAxkBAAI2f2KuAAFDf8weZSPvhJfqXj_NHirgAwACUb0xG6d2cUn78sce7lCKywEAAwIAA20AAyQE",
                            "file_unique_id": "AQADUb0xG6d2cUly",
                            "file_size": 15067,
                            "width": 245,
                            "height": 320
                        },
                        {
                            "file_id": "IAAxkBAAI2f2KuAAFDf8weZSPvhJfqXj_NHirgAwACUb0xG6d2cUn78sce7lCKywEAAwIAA3gAAyQE",
                            "file_unique_id": "AQADUb0xG6d2cUl9",
                            "file_size": 51944,
                            "width": 612,
                            "height": 800},
                        {
                            "file_id": "IAAxkBAAI2f2KuAAFDf8weZSPvhJfqXj_NHirgAwACUb0xG6d2cUn78sce7lCKywEAAwIAA3kAAyQE",
                            "file_unique_id": "AQADUb0xG6d2cUl-",
                            "file_size": 85690,
                            "width": 979,
                            "height": 1280
                        }
                    ]
                },
                "text": "12345"
            }
        }
    )


@pytest.fixture
def request_body_without_message():
    return StandardBodySchema(
        **{
            "update_id": 123,
        }
    )


@pytest.fixture
def request_body_edited_message():
    return StandardBodySchema(
        **{
            "update_id": 123,
            "edited_message": {
                "message_id": 1,
                "from": {
                    "id": 134,
                    "is_bot": False,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "language_code": "ru"
                },
                "chat": {
                    "id": 134,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "type": "private"
                },
                "date": 12343,
                "text": "Test"
            }
        }
    )


@pytest.fixture
def request_body_voice_message():
    return StandardBodySchema(
        **{
            "update_id": 123,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 134,
                    "is_bot": False,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "language_code": "ru"
                },
                "chat": {
                    "id": 134,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "type": "private"
                },
                "date": 12343,
                "voice": {
                    "duration": 4,
                    "mime_type": "some_type",
                    "file_id": "some_file_id",
                }
            }
        }
    )


@pytest.fixture
async def message_service(db, request_body_message) -> MessageService:
    message_service = MessageService(db=db, request_body=request_body_message)
    await message_service.init()
    return message_service


@pytest.fixture
async def edited_message_service(db, request_body_edited_message) -> MessageService:
    message_service = MessageService(db=db, request_body=request_body_edited_message)
    await message_service.init()
    return message_service


@pytest.fixture
async def voice_message_service(db, request_body_voice_message) -> MessageService:
    message_service = MessageService(db=db, request_body=request_body_voice_message)
    await message_service.init()
    return message_service
