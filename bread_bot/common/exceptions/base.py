class BaseMessageException(ValueError):
    """Базовый тип исключения для обработки сообщений"""
    pass


class RaiseUpException(BaseMessageException):
    """Тип исключения, который сразу поднимается до клиента"""
    pass


class NextStepException(BaseMessageException):
    """Тип исключения, который провоцирует пройти дальше по шагам"""
    pass
