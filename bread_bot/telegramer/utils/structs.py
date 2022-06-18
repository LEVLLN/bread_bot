from enum import Enum

TRIGGER_WORDS = [
    "хлебушек",
    "хлеб",
    "bread_bot"
]

DEFAULT_PREFIX = [
    "",
    "тупа",
    "скорее всего",
    "вероятно",
    "ля,",
    "ха-ха,",
    "ха,",
]
ERROR_CHAT_MESSAGES = [
    "Что-то сломалось, напишите создателю",
    "Ты точно правильно команду ввёл?",
]
DEFAULT_UNKNOWN_MESSAGE = [
    "Не знаю, что ответить",
    "Мне создатель запретил на такое отвечать",
    "Какой ты оригинальный, диву даюсь."
]


class StatsEnum(Enum):
    TOTAL_CALL_SLUG = "Вызвал бота"
    EDITOR = "Редактировал сообщения"
    FLUDER = "Написал сообщение"
    QUOTER = "Просил цитату"
    EVIL_INSULT = "Просил оскорбить на английском"
    INSULTER = "Просил оскорбить"
    VOICER = "Прислал голосовых"
    ADD_CONTENT = "Добавил контент"
    DELETE_CONTENT = "Удалил контент"
    CALLED_WHO = "Вызвал команду 'кто'"
    CALLED_TOP = "Вызвал команду 'топ'"
    CATCH_TRIGGER = "Попался на триггер"
    CATCH_SUBSTRING = "Попался на подстроку"


class LocalMemeTypesEnum(Enum):
    MEME_NAMES = "Привязки"
    UNKNOWN_MESSAGE = "Фразы на отсутствующие команды"
    FREE_WORDS = "Триггеры"
    SUBSTRING_WORDS = "Подстроки"
    REMEMBER_PHRASE = "Ключевые фразы"
    RUDE_WORDS = "Грубые фразы"


class LocalMemeDataTypesEnum(Enum):
    TEXT = "data"
    VOICE = "data_voice"
    PHOTO = "data_photo"


class PropertiesEnum(Enum):
    BAD_VOICES = "Плохие звуки"
    ANSWER_TO_EDIT = "Ответ на редактирование"
    DIGITS = "Цифры"
