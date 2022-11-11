from functools import cached_property

from bread_bot.telegramer.schemas.commands import CommandSettingsSchema
from bread_bot.telegramer.utils.structs import (
    AdminCommandsEnum,
    EntertainmentCommandsEnum,
    MemberCommandsEnum,
    CommandAnswerParametersEnum,
    CommandKeyValueParametersEnum,
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
            alias="покажи",
            command=AdminCommandsEnum.SHOW,
            available_parameters=CommandAnswerParametersEnum.list(),
        ),
        CommandSettingsSchema(
            alias="добавь",
            command=AdminCommandsEnum.ADD,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_key_values=True,
        ),
        CommandSettingsSchema(
            alias="запомни",
            command=AdminCommandsEnum.REMEMBER,
            available_parameters=CommandKeyValueParametersEnum.list(),
            to_find_for_values=True,
        ),
        CommandSettingsSchema(
            alias="удали",
            command=AdminCommandsEnum.DELETE,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_values=True,
            to_find_for_key_values=True,
        ),
        CommandSettingsSchema(
            alias="процент срабатывания",
            command=AdminCommandsEnum.ANSWER_CHANCE,
            to_find_for_values=True,
        ),
        CommandSettingsSchema(
            alias="распространи",
            command=AdminCommandsEnum.PROPAGATE,
        ),
        CommandSettingsSchema(
            alias="голосовые",
            command=AdminCommandsEnum.SET_VOICE_TRIGGER,
        ),
        CommandSettingsSchema(
            alias="редактирование",
            command=AdminCommandsEnum.SET_EDITED_TRIGGER,
        ),
        CommandSettingsSchema(
            alias="статистика",
            command=MemberCommandsEnum.STATS,
        ),
        CommandSettingsSchema(
            alias="парочка",
            command=MemberCommandsEnum.COUPLE,
        ),
        CommandSettingsSchema(
            alias="топ",
            command=MemberCommandsEnum.TOP,
        ),
        CommandSettingsSchema(
            alias="кто",
            command=MemberCommandsEnum.WHO,
        ),
        CommandSettingsSchema(
            command=EntertainmentCommandsEnum.CHANCE,
            alias="вероятность"
        ),
        CommandSettingsSchema(
            alias="help",
            command=EntertainmentCommandsEnum.HELP,
        ),
        CommandSettingsSchema(
            alias="выбери",
            command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
            to_find_for_values_list=True,
        ),
        CommandSettingsSchema(
            alias="цитата",
            command=EntertainmentCommandsEnum.GQUOTE,
        ),
        CommandSettingsSchema(
            alias="insult",
            command=EntertainmentCommandsEnum.INSULT,
        ),
        CommandSettingsSchema(
            alias="анекдот",
            command=EntertainmentCommandsEnum.JOKE,
        ),
        CommandSettingsSchema(
            alias="совет",
            command=EntertainmentCommandsEnum.ADVICE,
        ),
    )

    @cached_property
    def alias_list(self) -> list[str]:
        return [command_settings.alias for command_settings in self._COMMAND_SETTINGS]

    @cached_property
    def alias_to_command(self) -> dict[str, str]:
        return {
            command_settings.alias: command_settings.command.value for command_settings in self._COMMAND_SETTINGS
        }

    @cached_property
    def command_to_alias(self) -> dict[str, str]:
        return {
            command_settings.command.value: command_settings.alias for command_settings in self._COMMAND_SETTINGS
        }

    @cached_property
    def command_to_settings(self) -> dict[str, CommandSettingsSchema]:
        return {
            command_settings.command.value: command_settings for command_settings in self._COMMAND_SETTINGS
        }

    @cached_property
    def alias_to_settings(self) -> dict[str, CommandSettingsSchema]:
        return {
            command_settings.alias: command_settings for command_settings in self._COMMAND_SETTINGS
        }

    @cached_property
    def parameters_value_to_enum(self):
        return {
            parameter.value: parameter
            for parameter in (CommandKeyValueParametersEnum.list() + CommandAnswerParametersEnum.list())
        }
