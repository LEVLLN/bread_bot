import os
from enum import Enum

BOT_NAME = os.getenv("BOT_NAME", "Хлеб")
ALTER_NAMES = os.getenv("ALTER_NAMES", "хлебушек,хлеб,bread_bot")
TRIGGER_WORDS = [BOT_NAME.lower()] + ALTER_NAMES.split(",")


class AnswerEntityReactionTypesEnum(str, Enum):
    TRIGGER = "TRIGGER"
    SUBSTRING = "SUBSTRING"


class AnswerEntityContentTypesEnum(str, Enum):
    TEXT = "TEXT"
    VOICE = "VOICE"
    PICTURE = "PICTURE"
    ANIMATION = "ANIMATION"
    VIDEO = "VIDEO"
    VIDEO_NOTE = "VIDEO_NOTE"
    STICKER = "STICKER"


class AdminCommandsEnum(str, Enum):
    SHOW = "SHOW"
    ADD = "ADD"
    REMEMBER = "REMEMBER"
    REMEMBER_TRIGGER = "REMEMBER_TRIGGER"
    DELETE = "DELETE"
    ANSWER_CHANCE = "SHOW_ANSWER_CHANCE"
    SET_ANSWER_CHANCE = "SET_ANSWER_CHANCE"
    PROPAGATE = "PROPAGATE"
    SET_VOICE_TRIGGER = "SET_VOICE_TRIGGER"
    SET_EDITED_TRIGGER = "SET_EDITED_TRIGGER"
    CHECK_ANSWER = "CHECK_ANSWER"
    SAY = "SAY"
    SHOW_KEYS = "SHOW_KEYS"


class MemberCommandsEnum(str, Enum):
    WHO = "WHO"
    TOP = "TOP"
    COUPLE = "COUPLE"
    STATS = "STATS"
    CHANNEL = "CHANNEL"


class EntertainmentCommandsEnum(str, Enum):
    CHANCE = "CHANCE"
    HELP = "HELP"
    CHOOSE_VARIANT = "CHOOSE_VARIANT"
    RANDOM = "RANDOM"
    PAST_DATE = "PAST_DATE"
    FUTURE_DATE = "FUTURE_DATE"
    HOW_MANY = "HOW_MANY"


class IntegrationCommandsEnum(str, Enum):
    ADVICE = "ADVICE"
    QUOTE = "QUOTE"
    INSULT = "INSULT"
    JOKE = "JOKE"


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
    CommandAnswerParametersEnum.SUBSTRING: AnswerEntityReactionTypesEnum.SUBSTRING,
    CommandAnswerParametersEnum.SUBSTRING_LIST: AnswerEntityReactionTypesEnum.SUBSTRING,
    CommandAnswerParametersEnum.TRIGGER: AnswerEntityReactionTypesEnum.TRIGGER,
    CommandAnswerParametersEnum.TRIGGER_LIST: AnswerEntityReactionTypesEnum.TRIGGER,
}
