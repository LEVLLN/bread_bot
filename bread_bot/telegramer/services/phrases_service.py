import random
import re
from typing import Optional

from bread_bot.telegramer.models import Property, LocalMeme
from bread_bot.telegramer.utils import structs
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, StatsEnum, PropertiesEnum


class PhrasesServiceHandlerMixin:
    async def get_list_messages(
            self,
            meme_type: str = LocalMemeTypesEnum.UNKNOWN_MESSAGE.name) -> list:
        unknown_message_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if meme_type == LocalMemeTypesEnum.UNKNOWN_MESSAGE.name:
            unknown_messages = structs.DEFAULT_UNKNOWN_MESSAGE.copy()
        else:
            unknown_messages = list()
        if unknown_message_db is not None:
            unknown_messages.extend(unknown_message_db.data)
        return unknown_messages

    async def handle_free_words(self) -> Optional[str]:
        free_words_db: LocalMeme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name,
        )
        if free_words_db is None:
            return None
        message_text = self.message.text.lower().strip()
        if message_text not in free_words_db.data:
            return None
        value = free_words_db.data.get(message_text, 'упс!')
        if isinstance(value, list):
            return random.choice(value)
        elif isinstance(value, str):
            return value
        return None

    async def handle_rude_words(self):
        username = None
        if self.message.reply:
            username = f'@{self.message.reply.source.username}'
        rude_messages = await self.get_list_messages(
            meme_type=LocalMemeTypesEnum.RUDE_WORDS.name)
        if not rude_messages:
            return random.choice(structs.DEFAULT_UNKNOWN_MESSAGE)
        if username is not None:
            return f'{username}\n{random.choice(rude_messages)}'
        return random.choice(rude_messages)

    async def handle_substring_words(self) -> Optional[str]:
        substring_words_db = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
        )

        if substring_words_db is None or not substring_words_db.data:
            return None

        substring_words = substring_words_db.data
        substring_words_mask = self.composite_mask(
            collection=filter(lambda x: len(x) >= 3, substring_words.keys()),
            split=False,
        )
        regex = f'({substring_words_mask})'
        groups = re.findall(regex, self.message.text, re.IGNORECASE)

        if len(groups) > 0:
            substring_word = groups[0]
            value = substring_words.get(substring_word.lower().strip(), 'упс!')

            if isinstance(value, list):
                return random.choice(value)
            elif isinstance(value, str):
                return value

        return None

    async def handle_bind_words(self) -> Optional[str]:
        if self.command is None:
            return None

        bind_db: LocalMeme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name,
        )

        if bind_db is None \
                or self.command not in bind_db.data:
            return None

        message_prefix = random.choice(
            structs.DEFAULT_PREFIX + [self.command.capitalize(), ])
        message_value = random.choice(bind_db.data.get(self.command, []))
        return f'{message_prefix} {message_value}'

    async def handle_command_words(self) -> Optional[str]:
        if self.trigger_word and \
                self.command in structs.COMMANDS_MAPPER.keys():
            method = getattr(self, structs.COMMANDS_MAPPER[self.command])
            return await method()

    async def handle_unknown_words(self) -> Optional[str]:
        if self.trigger_word:
            unknown_messages = await self.get_list_messages()
            return random.choice(unknown_messages)
        return None

    async def handle_edited_words(self) -> Optional[str]:
        if self.is_edited and self.chat_db.is_edited_trigger:
            condition = Property.slug == PropertiesEnum.ANSWER_TO_EDIT.name
            editor_messages: Property = await Property.async_first(
                db=self.db,
                where=condition,
            )
            if editor_messages is None or not editor_messages.data:
                return None
            await self.count_stats(
                member_db=self.member_db,
                stats_enum=StatsEnum.EDITOR,
            )
            return random.choice(editor_messages.data)
        return None


class PhrasesServiceMixin:
    async def add_local_meme(self, meme_type: str) -> str:
        meme_name, value = self.params.strip().split('=', 1)
        meme_name = meme_name.lower().strip()
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            await LocalMeme.async_add_by_kwargs(
                self.db,
                chat_id=self.chat_id,
                type=meme_type,
                data={meme_name: [value]}
            )
            return f'Ура! У группы появились' \
                   f' {LocalMemeTypesEnum[meme_type].value}'

        data = local_meme.data.copy()

        if meme_name in data.keys():
            meme_list = data[meme_name].copy()
            meme_list.append(value)
            data[meme_name] = meme_list
        else:
            data[meme_name] = [value]

        local_meme.data = data
        await LocalMeme.async_add(self.db, local_meme)

        return self.COMPLETE_MESSAGE

    async def delete_local_meme(self, meme_type: str) -> str:
        value = self.params.strip().lower()
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            return f'У чата отсутствуют {LocalMemeTypesEnum[meme_type].value}'

        data = local_meme.data.copy()
        if value in data.keys():
            del data[value]
        else:
            return f'У чата отсутствуют {LocalMemeTypesEnum[meme_type].value}'

        local_meme.data = data
        await LocalMeme.async_add(self.db, local_meme)
        return self.COMPLETE_MESSAGE

    async def show_local_memes(self, meme_type: str) -> str:
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None or not local_meme.data:
            return f'У группы отсутствуют ' \
                   f'{LocalMemeTypesEnum[meme_type].value}'
        return '\n'.join(local_meme.data.keys())

    async def add_list_value(self, meme_type: str) -> str:
        value = self.params.strip()
        local_meme = await LocalMeme.get_local_meme(
            db=self.db,
            chat_id=self.chat_id,
            meme_type=meme_type,
        )
        if local_meme is None:
            await LocalMeme.async_add_by_kwargs(
                self.db,
                chat_id=self.chat_id,
                type=meme_type,
                data=[value]
            )
            return f'Ура! У группы появились ' \
                   f'{LocalMemeTypesEnum[meme_type].value}'

        if value in local_meme.data:
            return self.COMPLETE_MESSAGE

        data = local_meme.data.copy()
        data.append(value)
        local_meme.data = data
        await LocalMeme.async_add(self.db, local_meme)

        return self.COMPLETE_MESSAGE

    async def add_local_meme_name(self):
        return await self.add_local_meme(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name)

    async def add_local_substring(self):
        return await self.add_local_meme(
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name)

    async def add_local_free_word(self):
        return await self.add_local_meme(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)

    async def delete_local_meme_name(self):
        return await self.delete_local_meme(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name)

    async def delete_local_substring(self):
        return await self.delete_local_meme(
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name)

    async def delete_local_free_word(self):
        return await self.delete_local_meme(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)

    async def show_local_meme_names(self):
        return await self.show_local_memes(
            meme_type=LocalMemeTypesEnum.MEME_NAMES.name)

    async def show_local_substrings(self):
        return await self.show_local_memes(
            meme_type=LocalMemeTypesEnum.SUBSTRING_WORDS.name)

    async def show_local_free_words(self):
        return await self.show_local_memes(
            meme_type=LocalMemeTypesEnum.FREE_WORDS.name)

    async def add_unknown_answer(self) -> str:
        return await self.add_list_value(
            meme_type=LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
        )

    async def add_rude_phrase(self) -> str:
        return await self.add_list_value(
            meme_type=LocalMemeTypesEnum.RUDE_WORDS.name,
        )

    async def add_remember_phrase_as_key(self) -> str:
        if not self.message.reply or not self.params:
            return 'Выбери сообщение, которое запомнить'
        self.params = f'{self.message.reply.text}={self.params}'
        return await self.add_local_substring()

    async def add_remember_phrase_as_value(self) -> str:
        if not self.message.reply or not self.params:
            return 'Выбери сообщение, которое запомнить'
        self.params = f'{self.params}={self.message.reply.text}'
        return await self.add_local_substring()
