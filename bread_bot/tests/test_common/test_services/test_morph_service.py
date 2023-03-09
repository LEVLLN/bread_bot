import pytest

from bread_bot.common.models import DictionaryEntity
from bread_bot.common.services.morph_service import MorphService


async def test_morph_text(db, dictionary_entity_factory, member_service, message_service, mocker):
    text = "Только после 1830 Пушкин вплотную занялся прозой"
    mocker.patch(
        "bread_bot.common.services.morph_service.MorphService._get_maximum_words_to_replace", return_value=len(text)
    )
    for word in ["зариф", "прыгать", "мягкий", "2022", "головой", "до"]:
        await dictionary_entity_factory(chat_id=member_service.chat.id, value=word)
    assert await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)

    result = await MorphService(db, chat_id=member_service.chat.id).morph_text(text)
    assert result.startswith("Только до 1830 зариф вплотную прыгал")
    assert result.split()[-1] in ("головой", "головою")


async def test_add_value(db, member_service, message_service):
    await MorphService(db, chat_id=member_service.chat.id).add_values(["word1", "word2"])
    entities = await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)
    assert [e.value for e in entities] == ["word1", "word2"]


async def test_delete_value(db, member_service, message_service, dictionary_entity_factory):
    await dictionary_entity_factory(chat_id=member_service.chat.id, value="word1")
    await dictionary_entity_factory(chat_id=member_service.chat.id, value="word2")
    entities = await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)
    assert [e.value for e in entities] == ["word1", "word2"]
    await MorphService(db, chat_id=member_service.chat.id).delete_value("word2")
    entities = await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)
    assert [e.value for e in entities] == ["word1", ]


async def test_show_values(db, member_service, message_service, dictionary_entity_factory):
    await dictionary_entity_factory(chat_id=member_service.chat.id, value="word1")
    await dictionary_entity_factory(chat_id=member_service.chat.id, value="word2")
    entities = await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)
    assert [e.value for e in entities] == ["word1", "word2"]
    result = await MorphService(db, chat_id=member_service.chat.id).show_values()
    assert result == "word1, word2"
