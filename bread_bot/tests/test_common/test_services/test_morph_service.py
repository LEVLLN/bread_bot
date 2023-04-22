import pytest

from bread_bot.common.models import DictionaryEntity
from bread_bot.common.services.morph_service import MorphService


async def test_tokenize():
    text = """Утром:\n1)бегит\n2)хлеба ловить\n3)@писать\n\nВечером:\n1)анжуманя\n2)"писат"\n3)ловить\n👉"""
    result = MorphService.tokenize_text(text)
    assert result[0] == ["Утром", ":"]
    assert result[1] == ["1", ")", "бегит"]
    assert result[2] == ["2", ")", "хлеба", " ", "ловить"]
    assert result[3] == ["3", ")@", "писать"]
    assert result[4] == []
    assert result[5] == ["Вечером", ":"]
    assert result[6] == ["1", ")", "анжуманя"]
    assert result[7] == ["2", ')"', "писат", '"']
    assert result[8] == ["3", ")", "ловить"]
    assert result[9] == ["👉"]


@pytest.mark.parametrize(
    "text",
    [
        (
            "В чем разница между доктором физико-математических наук и большой пиццей?\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            ".\n"
            "Большая пицца способна накормить семью из четырех человек."
        ),
    ],
)
async def test_morph_corner_cases(db, dictionary_entity_factory, member_service, message_service, mocker, text):
    mocker.patch(
        "bread_bot.common.services.morph_service.MorphService._get_maximum_words_to_replace",
        return_value=100,
    )
    for word in [
        "2022",
    ]:
        await dictionary_entity_factory(chat_id=member_service.chat.id, value=word)
    assert await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)
    result = await MorphService(db, chat_id=member_service.chat.id).morph_text(text)
    assert result == text


async def test_morph_text(db, dictionary_entity_factory, member_service, message_service, mocker):
    text = "Только после 1830 Пушкин вплотную занялся \n-\n\n\nпрозой"
    mocker.patch(
        "bread_bot.common.services.morph_service.MorphService._get_maximum_words_to_replace",
        return_value=100,
    )
    for word in ["зариф", "прыгать", "мягкий", "2022", "голова", "до"]:
        await dictionary_entity_factory(chat_id=member_service.chat.id, value=word)
    assert await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)

    result = await MorphService(db, chat_id=member_service.chat.id).morph_text(text)
    assert result.startswith("Только до 1830 зариф вплотную прыгал")
    assert result.split()[-1] in ("головой", "головою")


@pytest.mark.parametrize(
    "line_number, min_of_morphed, max_of_morphed",
    [
        (0, 1, 1),
        (1, 1, 2),
        (2, 0, 0),
        (3, 1, 3),
        (4, 1, 1),
    ],
)
async def test_only_words(
    db, dictionary_entity_factory, member_service, message_service, line_number, min_of_morphed, max_of_morphed
):
    text = (
        "прозой прозой прозой \n прозой прозой прозой прозой прозой прозой-\n\nпрозой прозой прозой прозой прозой "
        "прозой прозой прозой прозой\nпрозой\nслово слово слово слово"
    )
    for word in ["зариф", "прыгать", "мягкий", "2022", "головой", "до"]:
        await dictionary_entity_factory(chat_id=member_service.chat.id, value=word)
    assert await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)

    result = await MorphService(db, chat_id=member_service.chat.id).morph_text(text)
    count = 0
    for word in result.splitlines()[line_number].split():
        if word in ("головой", "головою"):
            count += 1
    assert max_of_morphed >= count >= min_of_morphed


@pytest.mark.parametrize(
    "debug, expected",
    [
        (False, "слово\nслова\nслову\nслово\nсловом\nслове\nслова\nслов\nсловам\nслова\nсловами\nсловах"),
        (
            True,
            (
                "NOUN,inan,neut sing,nomn: слово\n"
                "NOUN,inan,neut sing,gent: слова\n"
                "NOUN,inan,neut sing,datv: слову\n"
                "NOUN,inan,neut sing,accs: слово\n"
                "NOUN,inan,neut sing,ablt: словом\n"
                "NOUN,inan,neut sing,loct: слове\n"
                "NOUN,inan,neut plur,nomn: слова\n"
                "NOUN,inan,neut plur,gent: слов\n"
                "NOUN,inan,neut plur,datv: словам\n"
                "NOUN,inan,neut plur,accs: слова\n"
                "NOUN,inan,neut plur,ablt: словами\n"
                "NOUN,inan,neut plur,loct: словах"
            ),
        ),
    ],
)
async def test_morph_word(db, dictionary_entity_factory, member_service, message_service, debug, expected):
    text = "Слово"
    result = MorphService.morph_word(word=text, debug=debug)
    assert result == expected


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
    assert [e.value for e in entities] == [
        "word1",
    ]


async def test_show_values(db, member_service, message_service, dictionary_entity_factory):
    await dictionary_entity_factory(chat_id=member_service.chat.id, value="word1")
    await dictionary_entity_factory(chat_id=member_service.chat.id, value="word2")
    entities = await DictionaryEntity.async_filter(db, DictionaryEntity.chat_id == member_service.chat.id)
    assert [e.value for e in entities] == ["word1", "word2"]
    result = await MorphService(db, chat_id=member_service.chat.id).show_values()
    assert result == "word1\nword2"
