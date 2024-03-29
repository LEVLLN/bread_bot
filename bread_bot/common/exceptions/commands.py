from bread_bot.common.exceptions.base import RaiseUpException, NextStepException


class CommandParseException(RaiseUpException):
    """Некорректные параметры, ключи и значения команд"""

    pass


class NotAvailableCommandException(NextStepException):
    """Отсутствуют аттрибуты для распознавания команды"""

    pass
