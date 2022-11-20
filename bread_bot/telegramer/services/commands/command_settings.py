from functools import cached_property

from bread_bot.telegramer.schemas.commands import CommandSettingsSchema
from bread_bot.telegramer.utils.structs import (
    AdminCommandsEnum,
    EntertainmentCommandsEnum,
    MemberCommandsEnum,
    CommandAnswerParametersEnum, IntegrationCommandsEnum,
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
        # ADMIN COMMANDS
        CommandSettingsSchema(
            aliases=["покажи", ],
            command=AdminCommandsEnum.SHOW,
            available_parameters=CommandAnswerParametersEnum.list(),
            description="Показывает сохраненные данные",
            examples=[
                "Хлеб покажи подстроки",
                "Хлеб покажи триггеры"
            ]
        ),
        CommandSettingsSchema(
            aliases=["добавь", ],
            command=AdminCommandsEnum.ADD,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_key_values=True,
            description="Добавление указанных данных",
            examples=[
                "Хлеб добавь подстроку my_key=my_value",
                "Хлеб добавь триггер my_key=my_value",
            ]
        ),
        CommandSettingsSchema(
            aliases=["запомни", "запомни значение", "запомни подстроку", "подстрока"],
            command=AdminCommandsEnum.REMEMBER,
            to_find_for_values=True,
            to_find_for_values_list=True,
            description="Запоминает как подстроку из сообщения в ответе",
            examples=[
                "Хлеб запомни my_key",
                "Хлеб запомни значение my_key",
                "Хлеб подстрока my_key",
                "Хлеб запомни my_key1, my_key2, my_key3"
            ]
        ),
        CommandSettingsSchema(
            aliases=["запомни триггер", "триггер"],
            command=AdminCommandsEnum.REMEMBER_TRIGGER,
            to_find_for_values=True,
            to_find_for_values_list=True,
            description="Запоминает как триггер из сообщения в ответе",
            examples=[
                "Хлеб запомни триггер my_key",
                "Хлеб триггер my_key",
                "Хлеб триггер my_key1, my_key2, my_key3"
            ]
        ),
        CommandSettingsSchema(
            aliases=["удали", ],
            command=AdminCommandsEnum.DELETE,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_values=True,
            to_find_for_key_values=True,
            description="Удаляет указанные данные",
            examples=[
                "Хлеб удали подстроки my_key",
                "Хлеб удали триггер my_key",
                "Хлеб удали подстроки my_key=my_value",
                "Хлеб удали подстроки my_key_1, my_key_2, my_key_3",
            ]
        ),
        CommandSettingsSchema(
            aliases=["процент срабатывания", "процент"],
            command=AdminCommandsEnum.ANSWER_CHANCE,
            to_find_for_values=True,
            description="Показ / Установка процента срабатывания подстрок",
            examples=[
                "Хлеб процент",
                "Хлеб процент 15",
            ]
        ),
        # MEMBER COMMANDS
        CommandSettingsSchema(
            aliases=["статистика", "стата"],
            command=MemberCommandsEnum.STATS,
            description="(Временно недоступно) - Показ статистики"
        ),
        CommandSettingsSchema(
            aliases=["парочка", "пара", ],
            command=MemberCommandsEnum.COUPLE,
            description="Образование пары из двух участников группы",
            examples=[
                "Хлеб парочка",
                "Хлеб парочка хороших людей",
            ]
        ),
        CommandSettingsSchema(
            aliases=["топ", ],
            command=MemberCommandsEnum.TOP,
            description="Формирование топ 10 из участников группы",
            examples=[
                "Хлеб топ",
                "Хлеб топ хороших людей",
            ]
        ),
        CommandSettingsSchema(
            aliases=["кто", "у кого", "кем", "с кем", "кого", "кому", "о ком", "чья", "чьё", "чей", "чье"],
            command=MemberCommandsEnum.WHO,
            description="Выбор случайного участника группы",
            examples=[
                "Хлеб кто хороший человек?",
                "Хлеб с кем веселее всего?",
            ]
        ),
        CommandSettingsSchema(
            command=EntertainmentCommandsEnum.CHANCE,
            aliases=["вероятность", "шанс"],
            description="Выдача вероятности события случайным образом",
            examples=[
                "Хлеб вероятность события N",
            ]
        ),
        CommandSettingsSchema(
            aliases=["help", "хелп", "помощь"],
            command=EntertainmentCommandsEnum.HELP,
            description="Помощь. Если к 'help' добавить имя команды, то будут отображены подробности запуска",
            examples=[
                "Хлеб help",
                "Хлеб help запомни",
            ]
        ),
        CommandSettingsSchema(
            aliases=["выбери", "выбор"],
            command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
            to_find_for_values_list=True,
            description="Выбор случайного значения из перечисленных",
            examples=[
                "Хлеб выбери 1, 2, 3, 4",
                "Хлеб выбери 1 или 2 или 3 или 4",
            ]
        ),
        CommandSettingsSchema(
            aliases=["цитата", "цит"],
            command=IntegrationCommandsEnum.QUOTE,
            description="Получение мудрой цитаты",
            examples=[
                "Хлеб цитата",
            ]
        ),
        CommandSettingsSchema(
            aliases=["insult", ],
            command=IntegrationCommandsEnum.INSULT,
            description="Оскорбление по английски на владельца сообщения из ответа",
            examples=[
                "Хлеб insult"
            ]
        ),
        CommandSettingsSchema(
            aliases=["анекдот", "шутка", "анек"],
            command=IntegrationCommandsEnum.JOKE,
            description="Получение анекдота",
            examples=[
                "Хлеб анекдот"
            ]
        ),
        CommandSettingsSchema(
            aliases=["совет", ],
            command=IntegrationCommandsEnum.ADVICE,
            description="Получение совета",
            examples=[
                "Хлеб совет",
                "Хлеб совет хорошим людям",
            ]
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

    @property
    def command_settings(self):
        return self._COMMAND_SETTINGS
