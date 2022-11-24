import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from bread_bot.main.database.base import DeclarativeBase
from bread_bot.common.schemas.telegram_messages import StandardBodySchema
from bread_bot.common.services.member_service import MemberService
from bread_bot.common.services.messages.message_service import MessageService


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
def reply_gif():
    return StandardBodySchema(
        **{
            "update_id": 958907794,
            "message": {
                "message_id": 35506,
                "from": {
                    "id": 296382623,
                    "is_bot": False,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "language_code": "ru"
                },
                "chat": {
                    "id": 296382623,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "type": "private"
                },
                "date": 1669076487,
                "reply_to_message": {
                    "message_id": 35490,
                    "from": {
                        "id": 296382623, "is_bot": False,
                        "first_name": "Tester",
                        "last_name": "Testerov",
                        "username": "Test_test",
                        "language_code": "ru"},
                    "chat": {
                        "id": 296382623,
                        "first_name": "Tester",
                        "last_name": "Testerov",
                        "username": "Test_test",
                        "type": "private"
                    },
                    "date": 1669076003,
                    "animation": {
                        "file_name": "scrubs-dr-perrycox.mp4",
                        "mime_type": "video/mp4",
                        "duration": 2, "width": 220,
                        "height": 220, "thumb": {
                            "file_id": "AAMCBAADGQEAAoqiY3wUIwAByXTLsz_tohgT0iQnyDpaAAIMAwAC5O4NUyOsp4F0bTr0AQAHbQADKwQ",
                            "file_unique_id": "AQADDAMAAuTuDVNy",
                            "file_size": 7292, "width": 220,
                            "height": 220},
                        "file_id": "CgACAgQAAxkBAAKKomN8FCMAAcl0y7M_7aIYE9IkJ8g6WgACDAMAAuTuDVMjrKeBdG069CsE",
                        "file_unique_id": "AgADDAMAAuTuDVM",
                        "file_size": 49283},
                    "document": {
                        "file_name": "scrubs-dr-perrycox.mp4",
                        "mime_type": "video/mp4",
                        "thumb": {
                            "file_id": "AAMCBAADGQEAAoqiY3wUIwAByXTLsz_tohgT0iQnyDpaAAIMAwAC5O4NUyOsp4F0bTr0AQAHbQADKwQ",
                            "file_unique_id": "AQADDAMAAuTuDVNy",
                            "file_size": 7292, "width": 220,
                            "height": 220
                        },
                        "file_id": "CgACAgQAAxkBAAKKomN8FCMAAcl0y7M_7aIYE9IkJ8g6WgACDAMAAuTuDVMjrKeBdG069CsE",
                        "file_unique_id": "AgADDAMAAuTuDVM",
                        "file_size": 49283
                    }
                },
                "text": "Кек"}}
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
def reply_photo_with_caption():
    return StandardBodySchema(
        **{
            "update_id": 958895851,
            "message": {
                "message_id": 34387,
                "from": {
                    "id": 296382623,
                    "is_bot": False,
                    "first_name": "Tester",
                    "last_name": "Testerov",
                    "username": "Test_test",
                    "language_code": "en"},
                "chat": {
                    "id": 296382623,
                    'first_name': 'Tester',
                    'last_name': 'Testerov',
                    'username': 'Test_test',
                    "type": "private"
                },
                "date": 1668554167,
                "reply_to_message": {
                    "message_id": 34386,
                    "from": {
                        "id": 296382623,
                        "is_bot": False,
                        'first_name': 'Tester',
                        'last_name': 'Testerov',
                        'username': 'Test_test',
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 296382623,
                        'first_name': 'Tester',
                        'last_name': 'Testerov',
                        'username': 'Test_test',
                        "type": "private"
                    },
                    "date": 1668552671,
                    "photo": [
                        {
                            "file_id": "AgACAgIAAxkBAAKGUmN0F99KZ-AAKRwjEbDXugS4arUhjBh3b3AQADAgADcwADKwQ",
                            "file_unique_id": "AQADkcIxGw17oEt4",
                            "file_size": 2105,
                            "width": 71,
                            "height": 90
                        },
                        {
                            "file_id": "AgACAgIAAxkBAAKGUmN0F99KZ-AAKRwjEbDXugS4arUhjBh3b3AQADAgADbQADKwQ",
                            "file_unique_id": "AQADkcIxGw17oEty",
                            "file_size": 31202,
                            "width": 252,
                            "height": 320},
                        {
                            "file_id": "AgACAgIAAxkBAAKGUmN0F99KZ-AAKRwjEbDXugS4arUhjBh3b3AQADAgADeAADKwQ",
                            "file_unique_id": "AQADkcIxGw17oEt9",
                            "file_size": 80331,
                            "width": 475,
                            "height": 604
                        }
                    ],
                    "caption": "some_message_good"
                },
                "text": "lololol"
            }
        }
    )


@pytest.fixture
def reply_sticker():
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
                    "sticker": {
                        "width": 512,
                        "height": 512,
                        "emoji": "🤨",
                        "set_name": "kz_meme",
                        "is_animated": False,
                        "is_video": False,
                        "thumb": {
                            "file_id": "AAMCAgADGQEAAja1Yq-UNR6YPAf6qnuwQiapV9kWpW0AAn4BAAJ0-FQb4PyXRewndEgBAAdtAAMkBA",
                            "file_unique_id": "AQADfgEAAnT4VBty", "file_size": 17784, "width": 320, "height": 320
                        },
                        "file_id": "CAACAgIAAxkBAAI2tWKvlDUemDwH-qp7sEImqVfZFqVtAAJ-AQACdPhUG-D8l0XsJ3RIJAQ",
                        "file_unique_id": "AgADfgEAAnT4VBs",
                        "file_size": 28628
                    }
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
async def message_service(request_body_message) -> MessageService:
    message_service = MessageService(request_body=request_body_message)
    yield message_service


@pytest.fixture
async def member_service(db, message_service) -> MemberService:
    member_service = MemberService(db=db, message=message_service.message)
    await member_service.process()
    yield member_service


@pytest.fixture
async def edited_message_service(request_body_edited_message) -> MessageService:
    message_service = MessageService(request_body=request_body_edited_message)
    yield message_service


@pytest.fixture
async def voice_message_service(request_body_voice_message) -> MessageService:
    message_service = MessageService(request_body=request_body_voice_message)
    yield message_service
