from bread_bot.telegramer.services.processors.base_message_processor import MessageProcessor
from bread_bot.telegramer.utils.structs import StatsEnum


class CommandMessageProcessor(MessageProcessor):
    # Соотношение команд к методам
    METHODS_MAP = NotImplemented
    # Сообщения об успехе
    COMPLETE_MESSAGES = ["Сделал", "Есть, сэр!", "Выполнено", "Принял"]

    @property
    async def condition(self) -> bool:
        return self.trigger_word and self.command is not None and self.command in self.METHODS_MAP

    async def process(self):
        await self.count_stats(StatsEnum.TOTAL_CALL_SLUG)
        await self.parse_command(list(self.METHODS_MAP.keys()))
        return await super(CommandMessageProcessor, self).process()

    async def _process(self):
        method = getattr(self, self.METHODS_MAP[self.command])
        return await method()
