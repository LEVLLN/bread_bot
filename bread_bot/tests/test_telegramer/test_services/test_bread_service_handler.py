import asyncio
import json
import unittest
from unittest import mock

from httpx import Response
from sqlalchemy import and_

from bread_bot.telegramer.models import LocalMeme, Chat, Property, Member, \
    Stats
from bread_bot.telegramer.schemas.api_models import ForismaticQuote
from bread_bot.telegramer.schemas.telegram_messages import \
    StandardBodySchema, MemberSchema, VoiceSchema, MessageSchema
from bread_bot.telegramer.services.bread_service_handler import \
    BreadServiceHandler
from bread_bot.telegramer.services.telegram_client import TelegramClient
from bread_bot.telegramer.utils.structs import LocalMemeTypesEnum, \
    PropertiesEnum
from bread_bot.utils.testing_tools import init_async_session


class BuildMessageTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = asyncio.run(init_async_session())
        cls.telegram_client = TelegramClient()
        cls.default_return_value = Response(
            status_code=200,
            content=json.dumps({'some_key': 'some_value'})
        )
        cls.default_message = StandardBodySchema(
            **{
                'update_id': 123,
                'message': {
                    'message_id': 1,
                    'from': {
                        'id': 134,
                        'is_bot': False,
                        'first_name': 'Tester',
                        'last_name': 'Testerov',
                        'username': 'Test_test',
                        'language_code': 'ru'
                    },
                    'chat': {
                        'id': 134,
                        'first_name': 'Tester',
                        'last_name': 'Testerov',
                        'username': 'Test_test',
                        'type': 'private'
                    },
                    'date': 12343,
                    'text': 'Test'
                }
            }
        )
        asyncio.run(LocalMeme.async_add_by_kwargs(
            db=cls.session,
            type=LocalMemeTypesEnum.FREE_WORDS.name,
            data={
                'some free word str': 'value',
                'some_free_word': ['default answer'],
                'some free word 3': {'default answer': 'value'},
                'some free word 2': ['default answer']
            },
            chat_id=cls.default_message.message.chat.id,
        ))
        asyncio.run(
            LocalMeme.async_add_by_kwargs(
                db=cls.session,
                type=LocalMemeTypesEnum.SUBSTRING_WORDS.name,
                data={
                    'my_substring': ['some_answer'],
                    'my_str': 'some_answer',
                    'ch': 'two_char_answer',
                },
                chat_id=cls.default_message.message.chat.id,
            )
        )

        asyncio.run(
            LocalMeme.async_add_by_kwargs(
                db=cls.session,
                type=LocalMemeTypesEnum.MEME_NAMES.name,
                chat_id=cls.default_message.message.chat.id,
                data={
                    'test_command': ['test_result'],
                }
            )

        )

    async def test_undefined_message(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'undefined message'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertIsNone(result)

    async def test_call_unknown_command(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'Хлеб'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertIsNone(result)

    async def test_call_simple_command(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'Хлеб help'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'https://telegra.ph/HlebushekBot-10-04-3'
        )

    async def test_edited_message(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'edited message'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=True,
        )
        # Without properties
        result = await handler.build_message()
        self.assertIsNone(result)
        # Enable Chat flag
        chat = await Chat.async_first(
            db=self.session,
            where=Chat.chat_id == message.chat.id,
        )
        chat.is_edited_trigger = True
        await Chat.async_add(self.session, chat)
        result = await handler.build_message()
        self.assertIsNone(result)
        # With property
        await Property.async_add_by_kwargs(
            self.session,
            slug=PropertiesEnum.ANSWER_TO_EDIT.name,
            data=['answer to edit message']
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'answer to edit message',
        )

    async def test_triggers(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'some_free_word'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'default answer'
        )

    async def test_dirty_triggers(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'some_free_word additional word'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertIsNone(result)

    async def test_substrings(self):
        message = self.default_message.message.copy(deep=True)
        message.text = 'Some message with my_substring expression'
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.build_message()
        self.assertEqual(
            result,
            'some_answer'
        )

    async def test_local_bind(self):
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        # Command without trigger word
        message.text = 'test_command'
        result = await handler.build_message()
        self.assertIsNone(result)
        # Command with trigger word
        message.text = 'Хлеб test_command'
        result = await handler.build_message()
        self.assertIn(
            'test_result',
            result
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service_handler.BreadServiceHandler.get_members')
    async def test_who_is(self, get_members_mock: mock.Mock):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        get_members_mock.return_value = [test_member, ]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some param'
        # Test self chat
        result = await handler.who_is()
        self.assertIn(
            f'{message.source.first_name} {message.source.last_name}',
            result,
        )
        # Test group chat
        handler.chat_id = -111111
        result = await handler.who_is()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service.BreadService.get_members')
    async def test_have_is(self, get_members_mock: mock.Mock):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        get_members_mock.return_value = [test_member, ]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some param'
        # Test self chat
        result = await handler.who_have_is()
        self.assertIn(
            f'{message.source.first_name} {message.source.last_name}',
            result,
        )
        # Test group chat
        handler.chat_id = -111111
        result = await handler.who_have_is()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service.BreadService.get_members')
    async def test_gey_double(self, get_members_mock: mock.Mock):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        test_member_two = MemberSchema(
            id=2,
            is_bot=False,
            first_name='Bill',
            last_name='Martin',
            username='somebill'
        )
        get_members_mock.return_value = [test_member, test_member_two]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_id = -111111
        result = await handler.gey_double()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )
        self.assertIn(
            f'{test_member_two.first_name} {test_member_two.last_name}',
            result,
        )

    @mock.patch('bread_bot.telegramer.services.'
                'bread_service.BreadService.get_members')
    async def test_top(self, get_members_mock: mock.Mock):
        test_member = MemberSchema(
            id=1,
            is_bot=False,
            first_name='Alex',
            last_name='Malex',
            username='somealex'
        )
        test_member_two = MemberSchema(
            id=2,
            is_bot=False,
            first_name='Bill',
            last_name='Martin',
            username='somebill'
        )
        get_members_mock.return_value = [test_member, test_member_two, None]
        message = self.default_message.message.copy(deep=True)
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_id = -111111
        handler.params = 'Some param'
        result = await handler.top()
        self.assertIn(
            f'{test_member.first_name} {test_member.last_name}',
            result,
        )
        self.assertIn(
            f'{test_member_two.first_name} {test_member_two.last_name}',
            result,
        )
        self.assertTrue(result.startswith('Топ'))
        self.assertIn(
            'Some param',
            result,
        )
        handler.chat_id = 111111
        handler.params = 'Some param'
        result = await handler.top()
        self.assertIn(
            f'{message.source.first_name} {message.source.last_name}',
            result,
        )
        self.assertTrue(result.startswith('Топ'))
        self.assertIn(
            'Some param',
            result,
        )

    async def test_num(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.get_num()
        self.assertIsInstance(result, str)
        self.assertTrue(
            result.isnumeric()
        )

    async def test_get_chance(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some event'
        result = await handler.get_chance()
        self.assertTrue(
            result.startswith('Есть вероятность')
        )
        self.assertIn(
            handler.params,
            result,
        )

    async def test_choose_variant(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'Some event0, Some event1'
        result = await handler.choose_variant()
        self.assertIn(
            result,
            handler.params
        )
        self.assertNotEqual(
            len(result),
            len(handler.params),
        )

    async def test_change_local_meme(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'key1=value1'
        # ADD
        result = await handler.add_local_meme_name()
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.MEME_NAMES.name,
            ),
        )
        self.assertEqual(
            local_meme.data['key1'],
            ['value1', ]
        )
        # SHOW
        handler.params = 'key1'
        result = await handler.show_local_meme_names()
        self.assertIn(
            'key1',
            result,
        )
        # DELETE
        handler.params = 'key1'
        result = await handler.delete_local_meme_name()
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.FREE_WORDS.name,
            ),
        )
        self.assertNotIn(
            'key1',
            local_meme.data,
        )

    async def test_change_substring(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        # ADD
        handler.params = 'key1=value1'
        result = await handler.add_local_substring()
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            ),
        )
        self.assertEqual(
            local_meme.data['key1'],
            ['value1', ]
        )
        # SHOW
        handler.params = 'key1'
        result = await handler.show_local_substrings()
        self.assertIn(
            'key1',
            result,
        )
        # DELETE
        handler.params = 'key1'
        result = await handler.delete_local_substring()
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.FREE_WORDS.name,
            ),
        )
        self.assertNotIn(
            'key1',
            local_meme.data,
        )

    async def test_change_unknown_answer(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        # ADD
        handler.params = 'value1'
        result = await handler.add_unknown_answer()
        self.assertEqual(
            result,
            'Ура! У группы появились Фразы на отсутствующие команды'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.UNKNOWN_MESSAGE.name,
            ),
        )
        self.assertEqual(
            local_meme.data,
            ['value1', ]
        )

    async def test_change_rude_answer(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        # ADD
        handler.params = 'value1'
        result = await handler.add_rude_phrase()
        self.assertEqual(
            result,
            'Ура! У группы появились Грубые фразы'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.RUDE_WORDS.name,
            ),
        )
        self.assertEqual(
            local_meme.data,
            ['value1', ]
        )

    async def test_change_free_word(self):
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        # ADD
        handler.params = 'key1=value1'
        result = await handler.add_local_free_word()
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.FREE_WORDS.name,
            ),
        )
        self.assertEqual(
            local_meme.data['key1'],
            ['value1', ]
        )
        # SHOW
        handler.params = 'key1'
        result = await handler.show_local_free_words()
        self.assertIn(
            'key1',
            result,
        )
        # DELETE
        handler.params = 'key1'
        result = await handler.delete_local_free_word()
        self.assertEqual(
            result,
            'Сделал'
        )
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.FREE_WORDS.name,
            ),
        )
        self.assertNotIn(
            'key1',
            local_meme.data,
        )

    @mock.patch('bread_bot.telegramer.services.bread_service_handler.'
                'ForismaticClient.get_quote_text')
    async def test_get_quote(self, get_quote_mock: mock.Mock):
        get_quote_mock.return_value = ForismaticQuote(
            text='Some text',
            author='Some author'
        )
        member = await Member.async_add_by_kwargs(
            db=self.session,
            username='user1',
            first_name='first_name_test',
            last_name='last_name_test'
        )
        chat = await Chat.async_add_by_kwargs(
            db=self.session,
            chat_id=55551,
            name='Some chat'
        )
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_db = chat
        handler.member_db = member
        handler.chat_id = chat.chat_id
        result = await handler.get_quote()
        self.assertEqual(
            result,
            'Some text\n\n© Some author'
        )
        stats = await Stats.async_first(
            db=self.session,
            where=and_(
                Stats.member_id == member.id,
                Stats.chat_id == chat.chat_id,
            )
        )
        self.assertEqual(
            stats.count,
            1
        )
        get_quote_mock.assert_called_once()

    @mock.patch('bread_bot.telegramer.services.telegram_client.'
                'TelegramClient.send_voice')
    async def test_send_to_voice(self, send_voice_mock: mock.Mock):
        send_voice_mock.return_value = True
        message = self.default_message.message.copy(deep=True)
        message.voice = VoiceSchema(
            duration=15,
            file_id='some_file_id'
        )
        chat = await Chat.async_add_by_kwargs(
            db=self.session,
            chat_id=55552,
            name='Some chat',
        )
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_db = chat
        # Not available for sending
        result = await handler.send_fart_voice()
        self.assertFalse(result)
        send_voice_mock.assert_not_called()
        # Not property
        chat.is_voice_trigger = True
        chat = await Chat.async_add(
            db=self.session,
            instance=chat,
        )
        handler.chat_db = chat
        self.assertTrue(chat.is_voice_trigger)
        result = await handler.send_fart_voice()
        self.assertIsNone(result)
        send_voice_mock.assert_not_called()
        # Success with property
        await Property.async_add_by_kwargs(
            db=self.session,
            slug=PropertiesEnum.BAD_VOICES.name,
            data=['Some_file_id']
        )
        result = await handler.send_fart_voice()
        self.assertIsNone(result)
        send_voice_mock.assert_called_once()
        send_voice_mock.assert_called_once_with(
            chat_id=handler.chat_id,
            voice_file_id='Some_file_id',
            reply_to=message.message_id,
        )

    async def test_set_edited_trigger(self):
        chat = await Chat.async_add_by_kwargs(
            db=self.session,
            chat_id=55553,
            name='Some chat',
        )
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_db = chat
        self.assertFalse(
            chat.is_edited_trigger,
        )
        # Enable flag
        result = await handler.set_edited_trigger()
        self.assertEqual(
            result,
            'Включено реагирование на редактирование сообщений'
        )
        chat = await Chat.async_first(
            db=self.session,
            where=Chat.id == chat.id,
        )
        self.assertTrue(chat.is_edited_trigger)
        # Disable flag
        result = await handler.set_edited_trigger()
        self.assertEqual(
            result,
            'Выключено реагирование на редактирование сообщений'
        )
        chat = await Chat.async_first(
            db=self.session,
            where=Chat.id == chat.id,
        )
        self.assertFalse(chat.is_edited_trigger)

    async def test_set_voice_trigger(self):
        chat = await Chat.async_add_by_kwargs(
            db=self.session,
            chat_id=55554,
            name='Some chat',
        )
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=self.default_message.message,
            db=self.session,
            is_edited=False,
        )
        handler.chat_db = chat
        self.assertFalse(
            chat.is_voice_trigger,
        )
        # Enable flag
        result = await handler.set_voice_trigger()
        self.assertEqual(
            result,
            'Включено реагирование на голосовые сообщения'
        )
        chat = await Chat.async_first(
            db=self.session,
            where=Chat.id == chat.id,
        )
        self.assertTrue(chat.is_voice_trigger)
        # Disable flag
        result = await handler.set_voice_trigger()
        self.assertEqual(
            result,
            'Выключено реагирование на голосовые сообщения'
        )
        chat = await Chat.async_first(
            db=self.session,
            where=Chat.id == chat.id,
        )
        self.assertFalse(chat.is_voice_trigger)

    async def test_remember_message(self):
        message = self.default_message.message.copy(deep=True)
        # Message without reply
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        result = await handler.add_remember_phrase()
        self.assertEqual(
            result,
            'Выбери сообщение, которое запомнить'
        )
        # Message with reply and params
        message.reply = MessageSchema(
            message_id=11110,
            chat=message.chat,
            source=message.source,
            text='Foo',
        )
        handler = BreadServiceHandler(
            client=self.telegram_client,
            message=message,
            db=self.session,
            is_edited=False,
        )
        handler.params = 'value1'
        result = await handler.add_remember_phrase()
        local_meme = await LocalMeme.async_first(
            db=self.session,
            where=and_(
                LocalMeme.chat_id == handler.chat_id,
                LocalMeme.type == LocalMemeTypesEnum.SUBSTRING_WORDS.name,
            ),
        )
        self.assertEqual(
            result,
            'Сделал',
        )
        self.assertIn(
            'foo',
            local_meme.data,
        )
        self.assertEqual(
            local_meme.data['foo'],
            ['value1', ]
        )
