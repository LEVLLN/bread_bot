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
