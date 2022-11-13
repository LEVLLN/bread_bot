from enum import Enum

TRIGGER_WORDS = [
    "хлебушек",
    "хлеб",
    "bread_bot"
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
    ADVICE = "Просил совет"
    EVIL_INSULT = "Просил оскорбить на английском"
    INSULTER = "Просил оскорбить"
    VOICER = "Прислал голосовых"
    ADD_CONTENT = "Добавил контент"
    DELETE_CONTENT = "Удалил контент"
    CALLED_WHO = "Вызвал команду 'кто'"
    CALLED_TOP = "Вызвал команду 'топ'"
    CATCH_TRIGGER = "Попался на триггер"
    CATCH_SUBSTRING = "Попался на подстроку"
    VALIDATION_ERROR = "Ошибка валидации"


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
    STICKER = "data_sticker"


class PropertiesEnum(Enum):
    BAD_VOICES = "Плохие звуки"
    ANSWER_TO_EDIT = "Ответ на редактирование"
    DIGITS = "Цифры"


class AnswerEntityTypesEnum(str, Enum):
    TRIGGER = "TRIGGER"
    SUBSTRING = "SUBSTRING"


class AdminCommandsEnum(str, Enum):
    SHOW = "SHOW"
    ADD = "ADD"
    REMEMBER = "REMEMBER"
    DELETE = "DELETE"
    ANSWER_CHANCE = "SHOW_ANSWER_CHANCE"
    SET_ANSWER_CHANCE = "SET_ANSWER_CHANCE"
    PROPAGATE = "PROPAGATE"
    SET_VOICE_TRIGGER = "SET_VOICE_TRIGGER"
    SET_EDITED_TRIGGER = "SET_EDITED_TRIGGER"


class MemberCommandsEnum(str, Enum):
    WHO = "WHO"
    TOP = "TOP"
    COUPLE = "COUPLE"
    STATS = "STATS"


class EntertainmentCommandsEnum(str, Enum):
    CHANCE = "CHANCE"
    HELP = "HELP"
    CHOOSE_VARIANT = "CHOOSE_VARIANT"
    GQUOTE = "QUOTE"
    INSULT = "INSULT"
    JOKE = "JOKE"
    ADVICE = "ADVICE"
    RANDOM = "RANDOM"


class IterEnum(str, Enum):
    @classmethod
    def list(cls):
        return [value for value in cls._member_map_.values()]


class CommandAnswerParametersEnum(IterEnum):
    SUBSTRING = "подстроку"
    SUBSTRING_LIST = "подстроки"
    TRIGGER = "триггер"
    TRIGGER_LIST = "триггеры"


ANSWER_ENTITY_MAP = {
    CommandAnswerParametersEnum.SUBSTRING: AnswerEntityTypesEnum.SUBSTRING,
    CommandAnswerParametersEnum.SUBSTRING_LIST: AnswerEntityTypesEnum.SUBSTRING,
    CommandAnswerParametersEnum.TRIGGER: AnswerEntityTypesEnum.TRIGGER,
    CommandAnswerParametersEnum.TRIGGER_LIST: AnswerEntityTypesEnum.TRIGGER,
}
