import pytest

from bread_bot.telegramer.models import Property, LocalMeme, Member, Chat, Stats


@pytest.fixture
async def property_factory(db):
    async def _factory(slug, data):
        return await Property.async_add_by_kwargs(db=db, slug=slug, data=data)
    yield _factory


@pytest.fixture
async def local_meme_factory(db):
    async def _factory(type, chat, data, data_photo=None, data_voice=None, data_sticker=None):
        return await LocalMeme.async_add_by_kwargs(db=db, type=type, data_photo=data_photo, data_sticker=data_sticker,
                                                   data_voice=data_voice, data=data, chat=chat)
    yield _factory


@pytest.fixture
async def member_factory(db):
    async def _factory(username, member_id):
        return await Member.async_add_by_kwargs(db=db, username=username, member_id=member_id)
    yield _factory


@pytest.fixture
async def chat_factory(db):
    async def _factory(chat_id, name):
        return await Chat.async_add_by_kwargs(db=db, chat_id=chat_id, name=name)
    yield _factory


@pytest.fixture
async def stats_factory(db):
    async def _factory(member_id, chat_id, slug, count):
        return await Stats.async_add_by_kwargs(db=db, member_id=member_id, chat_id=chat_id, slug=slug, count=count)
    yield _factory
