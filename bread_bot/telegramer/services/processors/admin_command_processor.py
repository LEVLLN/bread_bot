import random
from collections import defaultdict
from typing import Optional

from sqlalchemy import and_

from bread_bot.main.settings import SHOW_STR_LIMIT
from bread_bot.telegramer.models import LocalMeme, Chat, Member
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.services.processors.base_command_processor import CommandMessageProcessor
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum, LocalMemeDataTypesEnum


class AdminMessageProcessor(CommandMessageProcessor):
    METHODS_MAP = {
        "добавь": "add",
        "удали": "delete",
        "запомни": "remember",
        "покажи": "show",
        "процент срабатывания": "handle_answer_chance",
        "редактирование": "set_edited_trigger",
        "голосовые": "set_voice_trigger",
        "распространи в": "propagate_members_memes",
    }
    SUB_COMMAND_MAP = {
        "триггер": {"meme_type": LocalMemeTypesEnum.FREE_WORDS.name},
        "триггеры": {"meme_type": LocalMemeTypesEnum.FREE_WORDS.name},
        "подстроку": {"meme_type": LocalMemeTypesEnum.SUBSTRING_WORDS.name},
        "подстроки": {"meme_type": LocalMemeTypesEnum.SUBSTRING_WORDS.name},
        "как ключ": {"meme_type": LocalMemeTypesEnum.SUBSTRING_WORDS.name, "is_key": True},
        "как значение": {"meme_type": LocalMemeTypesEnum.SUBSTRING_WORDS.name, "is_key": False},
        "ключ": {"meme_type": LocalMemeTypesEnum.SUBSTRING_WORDS.name, "is_key": True},
        "значение": {"meme_type": LocalMemeTypesEnum.SUBSTRING_WORDS.name, "is_key": False},
        "ответ": {"meme_type": LocalMemeTypesEnum.UNKNOWN_MESSAGE.name},
        "ответы": {"meme_type": LocalMemeTypesEnum.UNKNOWN_MESSAGE.name},
        "оскорбление": {"meme_type": LocalMemeTypesEnum.RUDE_WORDS.name},
        "оскорбления": {"meme_type": LocalMemeTypesEnum.RUDE_WORDS.name},
    }

    async def _process(self):
        method = getattr(self, self.METHODS_MAP[self.command])
        sub_command_params, key, value = await self.parse_sub_command(self.SUB_COMMAND_MAP)
        if sub_command_params is not None:
            return await method(**sub_command_params, key=key, value=value)

        sub_command = self.command_params.split(" ")[0] if self.command_params else ""
        if sub_command in self.SUB_COMMAND_MAP:
            return await method(**self.SUB_COMMAND_MAP[sub_command])
        else:
            return await method(sub_command)

    async def add(self, meme_type: str,
                  key: str,
                  value: Optional[str],
                  data_key: str = LocalMemeDataTypesEnum.TEXT.value) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.ADD_CONTENT)
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=meme_type,
        )

        if local_meme is None:
            await LocalMeme.async_add_by_kwargs(
                db=self.db,
                chat_id=self.chat.chat_id,
                type=meme_type,
                **{data_key: {key: [value]} if value is not None else [key]}
            )
            return await self.get_text_answer(
                answer_text=f"Ура! У чата появились {LocalMemeTypesEnum[meme_type].value}"
            )

        data = getattr(local_meme, data_key)
        if data is not None:
            data_to_update = data.copy()
        else:
            data_to_update = {}

        if isinstance(data_to_update, dict) and key in data_to_update.keys():
            meme_list = data_to_update[key].copy()
            if value not in meme_list:
                meme_list.append(value)
                data_to_update[key] = meme_list
        elif isinstance(data_to_update, dict) and key not in data_to_update.keys():
            data_to_update[key] = [value]
        elif isinstance(data_to_update, list) and key and not value and key not in data_to_update:
            data_to_update.append(key)

        setattr(local_meme, data_key, data_to_update)
        await LocalMeme.async_add(self.db, local_meme)

        return await self.get_text_answer(
            answer_text=random.choice(self.COMPLETE_MESSAGES)
        )

    async def delete(self, meme_type: str, key: str, value: Optional[str]) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.DELETE_CONTENT)
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            return await self.get_text_answer(
                answer_text=f"У чата отсутствуют {LocalMemeTypesEnum[meme_type].value}"
            )

        data = local_meme.data.copy()

        if isinstance(data, dict) and key in data.keys():
            if value is not None:
                values = list(data[key])
                if value in values:
                    values.remove(value)
                    data[key] = list(values)
            else:
                del data[key]
        elif isinstance(data, dict):
            return await self.get_text_answer(
                answer_text=f"У чата отсутствуют {LocalMemeTypesEnum[meme_type].value}"
            )
        elif isinstance(data, list):
            if key and not value and key in data:
                data.remove(key)

        local_meme.data = data
        await LocalMeme.async_add(self.db, local_meme)
        return await self.get_text_answer(answer_text=random.choice(self.COMPLETE_MESSAGES))

    async def remember(self, meme_type: str, is_key: bool = None,
                       key: str = None, value: str = None) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.ADD_CONTENT)
        reply = self.message.reply
        data_key = LocalMemeDataTypesEnum.TEXT.value

        if not reply:
            return await self.get_text_answer(
                answer_text="Выбери сообщение, которое запомнить"
            )
        if is_key:
            key, value = reply.text, key
            if not key:
                return None
        else:
            if getattr(reply, "voice"):
                value = reply.voice.file_id
                data_key = LocalMemeDataTypesEnum.VOICE.value
            else:
                value = reply.text
        return await self.add(meme_type=meme_type, key=key, value=value, data_key=data_key)

    async def show(self, meme_type: str) -> Optional[TextAnswerSchema]:
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None or not local_meme.data:
            return await self.get_text_answer(
                answer_text=f"У группы отсутствуют {LocalMemeTypesEnum[meme_type].value}"
            )
        if isinstance(local_meme.data, dict):
            result_list = []
            for key, value in local_meme.data.items():
                result_list.append(f"{key} = [{'; '.join([item[:SHOW_STR_LIMIT] for item in value])}]")
            result = "\n".join(result_list)
        elif isinstance(local_meme.data, list):
            result = f"[{'; '.join([item for item in local_meme.data])}]"
        else:
            return await self.get_text_answer(
                answer_text=f"У группы отсутствуют {LocalMemeTypesEnum[meme_type].value}"
            )

        return await self.get_text_answer(
            answer_text=result
        )

    async def handle_answer_chance(self, chance_value: str):
        if chance_value == "":
            return await self.get_text_answer(
                answer_text=str(self.chat.answer_chance),
            )
        error_message = "Некорректное значение. Необходимо ввести число от 0 до 100"
        try:
            value = int(chance_value.strip())
        except ValueError:
            return await self.get_text_answer(
                answer_text=error_message
            )

        if value < 0 or value > 100:
            return await self.get_text_answer(
                answer_text=error_message
            )

        self.chat.answer_chance = value
        self.chat = await Chat.async_add(
            db=self.db,
            instance=self.chat,
        )
        if value < 0 or value > 100:
            return await self.get_text_answer(
                answer_text=error_message
            )
        return await self.get_text_answer(
            answer_text=random.choice(self.COMPLETE_MESSAGES)
        )

    async def set_edited_trigger(self, *args):
        self.chat.is_edited_trigger = not self.chat.is_edited_trigger
        self.chat = await Chat.async_add(
            db=self.db,
            instance=self.chat,
        )
        message = "Включено" if self.chat.is_edited_trigger else "Выключено"
        return await self.get_text_answer(
            answer_text=f"{message} реагирование на редактирование сообщений"
        )

    async def set_voice_trigger(self, *args):
        self.chat.is_voice_trigger = not self.chat.is_voice_trigger
        self.chat = await Chat.async_add(
            db=self.db,
            instance=self.chat,
        )
        message = "Включено" if self.chat.is_voice_trigger else "Выключено"
        return await self.get_text_answer(
            answer_text=f"{message} реагирование на голосовые сообщения"
        )

    async def propagate_members_memes(self, *args) -> Optional[TextAnswerSchema]:
        # TODO: Дописать тесты. Отрефакторить и оптимизировать функцию распространения
        if self.chat.chat_id < 0:
            return await self.get_text_answer(
                answer_text="Нельзя из чата копировать в другой чат. Только из личных сообщений с ботом!"
            )

        destination_chat: Chat = await Chat.async_first(
            db=self.db,
            where=Chat.name == self.command_params.strip(),
        )

        if destination_chat is None:
            return await self.get_text_answer(
                answer_text="Не найдено чата для отправки"
            )

        if destination_chat.chat_id > 0 \
                or destination_chat.chat_id == self.chat.chat_id:
            return await self.get_text_answer(
                answer_text="Невозможно копировать другим людям свои данные"
            )

        member: Member = await Member.async_first(
            db=self.db,
            where=Member.username == self.message.source.username,
            select_in_load=Member.chats
        )

        if not member:
            return await self.get_text_answer(
                answer_text="Что-то пошло не так"
            )

        if destination_chat.id not in [chat.chat_id for chat in member.chats]:
            return await self.get_text_answer(
                answer_text="Нет прав на указанный чат"
            )

        destination_local_memes = await LocalMeme.async_filter(
            db=self.db,
            where=and_(
                LocalMeme.chat_id == destination_chat.chat_id,
                LocalMeme.type != LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
                LocalMeme.type != LocalMemeTypesEnum.RUDE_WORDS.name,
                LocalMeme.type != LocalMemeTypesEnum.REMEMBER_PHRASE.name,
            )
        )
        source_local_memes = await LocalMeme.async_filter(
            db=self.db,
            where=and_(
                LocalMeme.chat_id == self.chat.chat_id,
                LocalMeme.type != LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
                LocalMeme.type != LocalMemeTypesEnum.RUDE_WORDS.name,
                LocalMeme.type != LocalMemeTypesEnum.REMEMBER_PHRASE.name,
            )
        )

        if not source_local_memes and not destination_local_memes:
            return await self.get_text_answer(
                answer_text="Не найдено данных для копирования"
            )

        data_to_add = defaultdict(lambda: defaultdict(set))
        local_memes_types = [d.type for d in destination_local_memes]
        update_list = []

        for source_meme in source_local_memes:
            for k, v in source_meme.data.items():
                data_to_add[source_meme.type][k] = v
            if source_meme.type not in local_memes_types:
                update_list.append(
                    LocalMeme(
                        type=source_meme.type,
                        data=source_meme.data,
                        chat_id=destination_chat.chat_id,
                    )
                )

        for local_meme in destination_local_memes:
            data = local_meme.data.copy()
            has_updated = False

            for k, v_set in data_to_add[local_meme.type].items():
                if k in data:
                    has_updated = True
                    result = set(data[k]).union(v_set)
                    data[k] = list(result)
                else:
                    has_updated = True
                    data[k] = list(v_set)

            if has_updated:
                local_meme.data = data
                update_list.append(local_meme)

        if not update_list:
            return await self.get_text_answer(
                answer_text="Нечего добавлять"
            )

        await LocalMeme.async_add_all(self.db, update_list)
        return await self.get_text_answer(
            answer_text=random.choice(self.COMPLETE_MESSAGES)
        )
