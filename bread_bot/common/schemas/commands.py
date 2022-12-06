from pydantic import BaseModel, Field, conlist

from bread_bot.common.utils.structs import (
    AdminCommandsEnum,
    MemberCommandsEnum,
    EntertainmentCommandsEnum,
    CommandAnswerParametersEnum,
    IntegrationCommandsEnum,
)


class CommandSchema(BaseModel):
    """
    Стандартная команда

    example: хлеб топ ->
        header = "хлеб"
        command = MemberCommandsEnum.TOP
        rest_text: ""
        raw_command: "топ"
    example: хлеб анекдот дня ->
        header = "хлеб"
        command = AdminCommandsEnum.JOKE
        rest_text = "дня"
        raw_command = "анекдот"
    """

    header: str = Field(..., title="Способ обращения к боту")
    command: AdminCommandsEnum | MemberCommandsEnum | EntertainmentCommandsEnum | IntegrationCommandsEnum
    raw_command: str = Field(..., title="Оригинальный текст команды")
    rest_text: str = Field("", title="Остаточный текст после обработки команды")


class ParameterCommandSchema(CommandSchema):
    """
    Команда с параметром

    example: хлеб покажи подстроки ->
        header = "хлеб"
        command = AdminCommandsEnum.SHOW
        parameter = CommandAnswerParametersEnum.SUBSTRING_LIST
        rest_text = ""
        raw_command = "покажи"
    """

    parameter: CommandAnswerParametersEnum


class ValueListCommandSchema(CommandSchema):
    """
    Команда со списком параметров

    example: хлеб выбери один или два или три или четыре ->
        header = "хлеб"
        command = EntertainmentCommandsEnum.CHOOSE_VARIANT
        valie_list = ["один", "два", "три", "четыре"]
        rest_text = ""
        raw_command = "выбери"
    """

    value_list: conlist(str, min_items=1)


class ValueCommandSchema(CommandSchema):
    """
    Команда со значением

    example: хлеб процент срабатывания 100 ->
        header = "хлеб"
        command = AdminCommandsEnum.ANSWER_CHANCE
        value = "100"
        rest_text = ""
        raw_command = "процент срабатывания"
    """

    value: str = Field(..., min_length=1)


class ValueParameterCommandSchema(ParameterCommandSchema):
    """
    Команда с параметром и значением

     example: хлеб запомни значение мое_значение ->
        header = "хлеб"
        command = AdminCommandsEnum.REMEMBER
        parameter = "значение"
        value = "мое_значение"
        rest_text = ""
        raw_command = "запомни"
    """

    value: str = Field(..., min_length=1)


class ValueListParameterCommandSchema(ParameterCommandSchema):
    """
    Команда с параметром и списком значений

     example: хлеб запомни значение один, два, три ->
        header = "хлеб"
        command = AdminCommandsEnum.REMEMBER
        parameter = "значение"
        value_list =["один", "два", "три"]
        rest_text = ""
        raw_command = "запомни"
    """

    value_list: list[str]


class KeyValueParameterCommandSchema(ValueParameterCommandSchema):
    """
    Команда с параметром, ключом и значением

     example: хлеб добавь триггер мой_ключ=мое_значение ->
        header = "хлеб"
        command = AdminCommandsEnum.ADD
        parameter = "триггер"
        key = "мой_ключ"
        value = "мое_значение"
        rest_text = ""
        raw_command = "добавь"
    """

    key: str = Field(..., min_length=1)


class CommandSettingsSchema(BaseModel):
    """
    Схема настройки команды
    """

    command: AdminCommandsEnum | EntertainmentCommandsEnum | MemberCommandsEnum | IntegrationCommandsEnum
    aliases: list[str] = Field(..., title="Список вызовов команды на русском языке")
    available_parameters: list[CommandAnswerParametersEnum] | None = Field(None, title="Допустимые параметры к команде")
    to_find_for_values_list: bool = Field(False, title="Ожидание списка значений")
    to_find_for_values: bool = Field(False, title="Ожидание одного значения")
    to_find_for_key_values: bool = Field(False, title="Ожидание структуры ключ=значение")
    description: str | None = None
    examples: list | None = None
