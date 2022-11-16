from functools import cached_property

from bread_bot.telegramer.schemas.commands import CommandSettingsSchema
from bread_bot.telegramer.utils.structs import (
    AdminCommandsEnum,
    EntertainmentCommandsEnum,
    MemberCommandsEnum,
    CommandAnswerParametersEnum,
)


class CommandSettings:
    """
    Singleton настроек команд в проекте
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CommandSettings, cls).__new__(cls)
        return cls.instance

    # Инициализация настройки команд
    _COMMAND_SETTINGS = (
        CommandSettingsSchema(
            aliases=["покажи", ],
            command=AdminCommandsEnum.SHOW,
            available_parameters=CommandAnswerParametersEnum.list(),
        ),
        CommandSettingsSchema(
            aliases=["добавь", ],
            command=AdminCommandsEnum.ADD,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_key_values=True,
        ),
        CommandSettingsSchema(
            aliases=["запомни", "запомни значение", "подстрока"],
            command=AdminCommandsEnum.REMEMBER,
            to_find_for_values=True,
            to_find_for_values_list=True,
        ),
        CommandSettingsSchema(
            aliases=["удали", ],
            command=AdminCommandsEnum.DELETE,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_values=True,
            to_find_for_key_values=True,
        ),
        CommandSettingsSchema(
            aliases=["процент срабатывания", "процент"],
            command=AdminCommandsEnum.ANSWER_CHANCE,
            to_find_for_values=True,
        ),
        CommandSettingsSchema(
            aliases=["распространи", ],
            command=AdminCommandsEnum.PROPAGATE,
        ),
        CommandSettingsSchema(
            aliases=["голосовые", ],
            command=AdminCommandsEnum.SET_VOICE_TRIGGER,
        ),
        CommandSettingsSchema(
            aliases=["редактирование", ],
            command=AdminCommandsEnum.SET_EDITED_TRIGGER,
        ),
        CommandSettingsSchema(
            aliases=["статистика", "стата"],
            command=MemberCommandsEnum.STATS,
        ),
        CommandSettingsSchema(
            aliases=["парочка", ],
            command=MemberCommandsEnum.COUPLE,
        ),
        CommandSettingsSchema(
            aliases=["топ", ],
            command=MemberCommandsEnum.TOP,
        ),
        CommandSettingsSchema(
            aliases=["кто", "у кого", "кем", "с кем", "кем", "кого", "кому", "о ком"],
            command=MemberCommandsEnum.WHO,
        ),
        CommandSettingsSchema(
            command=EntertainmentCommandsEnum.CHANCE,
            aliases=["вероятность", "шанс"]
        ),
        CommandSettingsSchema(
            aliases=["help", "хелп", "помощь"],
            command=EntertainmentCommandsEnum.HELP,
        ),
        CommandSettingsSchema(
            aliases=["выбери", "выбор"],
            command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
            to_find_for_values_list=True,
        ),
        CommandSettingsSchema(
            aliases=["цитата", "цит"],
            command=EntertainmentCommandsEnum.GQUOTE,
        ),
        CommandSettingsSchema(
            aliases=["insult", ],
            command=EntertainmentCommandsEnum.INSULT,
        ),
        CommandSettingsSchema(
            aliases=["анекдот", "шутка", "анек"],
            command=EntertainmentCommandsEnum.JOKE,
        ),
        CommandSettingsSchema(
            aliases=["совет", ],
            command=EntertainmentCommandsEnum.ADVICE,
        ),
    )

    @cached_property
    def alias_list(self) -> list[str]:
        result = []
        for command_settings in self._COMMAND_SETTINGS:
            result += command_settings.aliases
        return result

    @cached_property
    def alias_to_settings(self) -> dict[str, CommandSettingsSchema]:
        result = {}
        for command_settings in self._COMMAND_SETTINGS:
            for alias in command_settings.aliases:
                result[alias] = command_settings
        return result

    @cached_property
    def parameters_value_to_enum(self):
        return {
            parameter.value: parameter
            for parameter in CommandAnswerParametersEnum.list()
        }
