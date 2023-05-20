import pytest

from bread_bot.common.models import (
    AnswerEntity,
    Chat,
    DictionaryEntity,
    Member,
)
from bread_bot.common.utils.structs import AnswerEntityContentTypesEnum


@pytest.fixture
async def member_factory(db):
    async def _factory(username, member_id, **kwargs):
        return await Member.async_add_by_kwargs(db=db, username=username, member_id=member_id, **kwargs)

    return _factory


@pytest.fixture
async def chat_factory(db):
    async def _factory(chat_id, name):
        return await Chat.async_add_by_kwargs(db=db, chat_id=chat_id, name=name)

    return _factory


@pytest.fixture
async def text_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await AnswerEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            content_type=AnswerEntityContentTypesEnum.TEXT,
            pack_id=pack_id,
            **kwargs,
        )

    return _factory


@pytest.fixture
async def voice_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await AnswerEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            content_type=AnswerEntityContentTypesEnum.VOICE,
            pack_id=pack_id,
            **kwargs,
        )

    return _factory


@pytest.fixture
async def sticker_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await AnswerEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            content_type=AnswerEntityContentTypesEnum.STICKER,
            pack_id=pack_id,
            **kwargs,
        )

    return _factory


@pytest.fixture
async def photo_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await AnswerEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            content_type=AnswerEntityContentTypesEnum.PICTURE,
            pack_id=pack_id,
            **kwargs,
        )

    return _factory


@pytest.fixture
async def gif_entity_factory(db):
    async def _factory(key, value, reaction_type, pack_id, **kwargs):
        return await AnswerEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            content_type=AnswerEntityContentTypesEnum.ANIMATION,
            pack_id=pack_id,
            **kwargs,
        )

    return _factory


@pytest.fixture
async def answer_entity_factory(db):
    async def _factory(key, value, content_type, reaction_type, pack_id, **kwargs):
        return await AnswerEntity.async_add_by_kwargs(
            db=db,
            key=key,
            value=value,
            reaction_type=reaction_type,
            content_type=content_type,
            pack_id=pack_id,
            **kwargs,
        )

    return _factory


@pytest.fixture
async def dictionary_entity_factory(db):
    async def _factory(chat_id, value, **kwargs):
        return await DictionaryEntity.async_add_by_kwargs(
            db=db,
            chat_id=chat_id,
            value=value,
            **kwargs,
        )

    return _factory
