import pytest

from bread_bot.telegramer.models import (
    Property,
    LocalMeme,
    Member,
    Chat,
    Stats,
    TextEntity,
    VoiceEntity,
    StickerEntity,
    PhotoEntity, GifEntity,
)


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
    async def _factory(username, member_id, **kwargs):
        return await Member.async_add_by_kwargs(db=db, username=username, member_id=member_id, **kwargs)

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


@pytest.fixture
async def text_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await TextEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            pack_id=pack_id,
            **kwargs,
        )

    yield _factory


@pytest.fixture
async def voice_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await VoiceEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            pack_id=pack_id,
            **kwargs,
        )

    yield _factory


@pytest.fixture
async def sticker_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await StickerEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            pack_id=pack_id,
            **kwargs,
        )

    yield _factory


@pytest.fixture
async def photo_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await PhotoEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            pack_id=pack_id,
            **kwargs,
        )

    yield _factory


@pytest.fixture
async def gif_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await GifEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            pack_id=pack_id,
            **kwargs,
        )

    yield _factory
