from enum import Enum

TRIGGER_WORDS = ["хлебушек", "хлеб", "bread_bot"]


class AnswerEntityTypesEnum(str, Enum):
    TRIGGER = "TRIGGER"
    SUBSTRING = "SUBSTRING"


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
    CommandAnswerParametersEnum.SUBSTRING: AnswerEntityTypesEnum.SUBSTRING,
    CommandAnswerParametersEnum.SUBSTRING_LIST: AnswerEntityTypesEnum.SUBSTRING,
    CommandAnswerParametersEnum.TRIGGER: AnswerEntityTypesEnum.TRIGGER,
    CommandAnswerParametersEnum.TRIGGER_LIST: AnswerEntityTypesEnum.TRIGGER,
}
