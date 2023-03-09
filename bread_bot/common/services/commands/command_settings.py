from functools import cached_property

from bread_bot.common.schemas.commands import CommandSettingsSchema
from bread_bot.common.utils.structs import (
    AdminCommandsEnum,
    BOT_NAME,
    CommandAnswerParametersEnum,
    EntertainmentCommandsEnum,
    IntegrationCommandsEnum,
    MemberCommandsEnum,
)


class CommandSettings:
    """
    Singleton настроек команд в проекте
    """

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(CommandSettings, cls).__new__(cls)
        return cls.instance

    # Инициализация настройки команд
    _COMMAND_SETTINGS = (
        # ADMIN COMMANDS
        CommandSettingsSchema(
            aliases=[
                "покажи",
            ],
            command=AdminCommandsEnum.SHOW,
            available_parameters=CommandAnswerParametersEnum.list(),
            description="Показывает сохраненные данные",
            examples=[f"{BOT_NAME} покажи подстроки", f"{BOT_NAME} покажи триггеры"],
        ),
        CommandSettingsSchema(
            aliases=[
                "добавь",
            ],
            command=AdminCommandsEnum.ADD,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_key_values=True,
            description="Добавление указанных данных",
            examples=[
                f"{BOT_NAME} добавь подстроку my_key=my_value",
                f"{BOT_NAME} добавь триггер my_key=my_value",
            ],
        ),
        CommandSettingsSchema(
            aliases=[
                "запомни значение",
                "запомни подстроку",
                "подстрока",
                "запомни",
            ],
            command=AdminCommandsEnum.REMEMBER,
            to_find_for_values=True,
            to_find_for_values_list=True,
            description=(
                "[Надо выбрать сообщение в качестве ответа] Запоминает как подстроку из сообщения в ответе. Работает с "
                "картинками, картинками с описанием, анимациями, голосовыми, стикерами, текстом, видео, видео-кружками"
            ),
            examples=[
                f"{BOT_NAME} запомни my_key",
                f"{BOT_NAME} запомни значение my_key",
                f"{BOT_NAME} подстрока my_key",
                f"{BOT_NAME} запомни my_key1, my_key2, my_key3",
            ],
        ),
        CommandSettingsSchema(
            aliases=["запомни триггер", "триггер"],
            command=AdminCommandsEnum.REMEMBER_TRIGGER,
            to_find_for_values=True,
            to_find_for_values_list=True,
            description=(
                "[Надо выбрать сообщение в качестве ответа] Запоминает как триггер из сообщения в ответе. Работает с "
                "картинками, картинками с описанием, анимациями, голосовыми, стикерами, текстом, видео, видео-кружками"
            ),
            examples=[
                f"{BOT_NAME} запомни триггер my_key",
                f"{BOT_NAME} триггер my_key",
                f"{BOT_NAME} триггер my_key1, my_key2, my_key3",
            ],
        ),
        CommandSettingsSchema(
            aliases=[
                "удали",
            ],
            command=AdminCommandsEnum.DELETE,
            available_parameters=CommandAnswerParametersEnum.list(),
            to_find_for_values=True,
            to_find_for_key_values=True,
            description="Удаляет указанные данные",
            examples=[
                f"{BOT_NAME} удали подстроки my_key",
                f"{BOT_NAME} удали триггер my_key",
                f"{BOT_NAME} удали подстроки my_key=my_value",
            ],
        ),
        CommandSettingsSchema(
            aliases=["процент срабатывания", "процент"],
            command=AdminCommandsEnum.ANSWER_CHANCE,
            to_find_for_values=True,
            description="Показ / Установка процента срабатывания подстрок",
            examples=[
                f"{BOT_NAME} процент",
                f"{BOT_NAME} процент 15",
            ],
        ),
        CommandSettingsSchema(
            aliases=["проверь", "проверка", "check"],
            command=AdminCommandsEnum.CHECK_ANSWER,
            to_find_for_values=True,
            description=(
                "В чатах с маленьким процентом срабатывания команда дает возможность проверку отработки "
                "ответов на определенные триггеры или подстроки"
            ),
            examples=[
                f"{BOT_NAME} check моя_подстрока",
                f"{BOT_NAME} check мой_триггер",
                f"{BOT_NAME} проверь мой_триггер",
                f"{BOT_NAME} проверь моя_подстрока",
                f"{BOT_NAME} проверка мой_триггер",
                f"{BOT_NAME} проверка моя_подстрока",
            ],
        ),
        CommandSettingsSchema(
            aliases=["скажи", "say"],
            command=AdminCommandsEnum.SAY,
            to_find_for_values=True,
            description="Бот присылает строку, которую указали в качестве параметров.",
            examples=[
                f"{BOT_NAME} скажи Какой прекрасный день!",
                f"{BOT_NAME} say Какой прекрасный день!",
            ],
        ),
        CommandSettingsSchema(
            aliases=["покажи ключи", "show keys"],
            command=AdminCommandsEnum.SHOW_KEYS,
            description=(
                "[Надо выбрать сообщение в качестве ответа] Бот показывает перечень ключей на определенный контент"
            ),
            examples=[
                f"{BOT_NAME} покажи ключи",
            ],
        ),
        # MEMBER COMMANDS
        CommandSettingsSchema(
            aliases=["статистика", "стата"],
            command=MemberCommandsEnum.STATS,
            description="(Временно недоступно) - Показ статистики",
        ),
        CommandSettingsSchema(
            aliases=[
                "парочка",
                "пара",
            ],
            command=MemberCommandsEnum.COUPLE,
            description="Образование пары из двух участников группы",
            examples=[
                f"{BOT_NAME} парочка",
                f"{BOT_NAME} парочка хороших людей",
            ],
        ),
        CommandSettingsSchema(
            aliases=[
                "топ",
            ],
            command=MemberCommandsEnum.TOP,
            description="Формирование топ 10 из участников группы",
            examples=[
                f"{BOT_NAME} топ",
                f"{BOT_NAME} топ хороших людей",
            ],
        ),
        CommandSettingsSchema(
            aliases=[
                "кто",
                "у кого",
                "кем",
                "с кем",
                "кого",
                "кому",
                "о ком",
                "чья",
                "чьё",
                "чей",
                "чье",
            ],
            command=MemberCommandsEnum.WHO,
            description="Выбор случайного участника группы",
            examples=[
                f"{BOT_NAME} кто хороший человек?",
                f"{BOT_NAME} с кем веселее всего?",
            ],
        ),
        CommandSettingsSchema(
            aliases=["channel", "all", "канал"],
            command=MemberCommandsEnum.CHANNEL,
            description="Тегнуть всех участников в чате для привлечения внимания",
            examples=[
                f"{BOT_NAME} channel",
                f"{BOT_NAME} all",
                f"{BOT_NAME} канал",
            ],
        ),
        # ENTERTAINMENT COMMANDS
        CommandSettingsSchema(
            command=EntertainmentCommandsEnum.CHANCE,
            aliases=["вероятность", "шанс"],
            description="Выдача вероятности события случайным образом",
            examples=[
                f"{BOT_NAME} вероятность события N",
            ],
        ),
        CommandSettingsSchema(
            command=EntertainmentCommandsEnum.FUTURE_DATE,
            aliases=[
                "когда",
                "когда будет",
                "когда будут",
                "когда настанет",
                "когда настанут",
                "когда случится",
                "когда случатся",
                "когда произойдет",
                "когда произойдут",
                "когда наступит",
                "когда наступят",
            ],
            description="Выдача случайной даты из будущего на событие",
            examples=[
                f"{BOT_NAME} когда будет хороший день?",
            ],
        ),
        CommandSettingsSchema(
            command=EntertainmentCommandsEnum.HOW_MANY,
            aliases=[
                "сколько",
            ],
            description="Выдача случайного числа на событие",
            examples=[
                f"{BOT_NAME} сколько на планете ежей?",
            ],
        ),
        CommandSettingsSchema(
            command=EntertainmentCommandsEnum.PAST_DATE,
            aliases=[
                "когда был",
                "когда было",
                "когда была",
                "когда были",
                "когда настало",
                "когда настала",
                "когда настал",
                "когда настали",
                "когда наступило",
                "когда наступила",
                "когда наступил",
                "когда наступили",
                "когда случилось",
                "когда случилась",
                "когда случился",
                "когда случились",
                "когда произошло",
                "когда произошла",
                "когда произошел",
                "когда произошли",
            ],
            description="Выдача случайной даты из прошлого на событие",
            examples=[
                f"{BOT_NAME} когда были лучшие времена?",
                f"{BOT_NAME} когда произошли случайные события?",
            ],
        ),
        CommandSettingsSchema(
            aliases=["help", "хелп", "помощь"],
            command=EntertainmentCommandsEnum.HELP,
            description="Помощь. Если к 'help' добавить имя команды, то будут отображены подробности запуска",
            examples=[
                f"{BOT_NAME} help",
                f"{BOT_NAME} help запомни",
            ],
        ),
        CommandSettingsSchema(
            aliases=["выбери", "выбор"],
            command=EntertainmentCommandsEnum.CHOOSE_VARIANT,
            to_find_for_values_list=True,
            description="Выбор случайного значения из перечисленных",
            examples=[
                f"{BOT_NAME} выбери 1, 2, 3, 4",
                f"{BOT_NAME} выбери 1 или 2 или 3 или 4",
            ],
        ),
        CommandSettingsSchema(
            aliases=["бред", "давай"],
            command=EntertainmentCommandsEnum.REGENERATE_MESSAGE,
            description="[Надо выбрать сообщение в качестве ответа] заменяет сообщение на известные слова боту",
            examples=[
                f"{BOT_NAME} бред",
            ],
        ),
        CommandSettingsSchema(
            aliases=["добавь бред"],
            command=EntertainmentCommandsEnum.ADD_MORPH_ENTITIES,
            description="Наполнение словаря для бреда",
            to_find_for_values_list=True,
            examples=[
                f"{BOT_NAME} добавь бред слово1, слово2, слово3",
            ],
        ),
        CommandSettingsSchema(
            aliases=["удали бред"],
            command=EntertainmentCommandsEnum.DELETE_MORPH_ENTITY,
            description="Удаление указанного значения из бреда",
            to_find_for_values=True,
            examples=[
                f"{BOT_NAME} удали бред слово1",
            ],
        ),
        CommandSettingsSchema(
            aliases=["покажи бред"],
            command=EntertainmentCommandsEnum.SHOW_MORPH_ENTITIES,
            description="Показ списка сохраненных слов для бреда",
            examples=[
                f"{BOT_NAME} покажи бред",
            ],
        ),
        CommandSettingsSchema(
            aliases=["морф", "морфируй"],
            command=EntertainmentCommandsEnum.MORPH_WORD,
            to_find_for_values=True,
            description="Склоняет в разные формы слово",
            examples=[
                f"{BOT_NAME} морфируй слово",
                f"{BOT_NAME} морф слово",
            ],
        ),
        # INTEGRATION COMMANDS
        CommandSettingsSchema(
            aliases=["цитата", "цит"],
            command=IntegrationCommandsEnum.QUOTE,
            description="Получение мудрой цитаты",
            examples=[
                f"{BOT_NAME} цитата",
            ],
        ),
        CommandSettingsSchema(
            aliases=[
                "insult",
            ],
            command=IntegrationCommandsEnum.INSULT,
            description=(
                "[Надо выбрать сообщение в качестве ответа] Оскорбление по английски на владельца сообщения из ответа"
            ),
            examples=[f"{BOT_NAME} insult"],
        ),
        CommandSettingsSchema(
            aliases=["анекдот", "шутка", "анек"],
            command=IntegrationCommandsEnum.JOKE,
            description="Получение анекдота",
            examples=[f"{BOT_NAME} анекдот"],
        ),
        CommandSettingsSchema(
            aliases=[
                "совет",
            ],
            command=IntegrationCommandsEnum.ADVICE,
            description="Получение совета",
            examples=[
                f"{BOT_NAME} совет",
                f"{BOT_NAME} совет хорошим людям",
            ],
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
        return {parameter.value: parameter for parameter in CommandAnswerParametersEnum.list()}

    @property
    def command_settings(self):
        return self._COMMAND_SETTINGS
