import datetime
import time

import pytest

from bread_bot.common.exceptions.base import NextStepException
from bread_bot.common.models import Chat, Member, ChatToMember
from bread_bot.common.services.member_service import MemberService
from bread_bot.common.services.messages.message_service import MessageService


class TestMessageHandler:
    async def test_has_message(self, request_body_message):
        handler = MessageService(request_body=request_body_message)
        assert handler.has_message is True

    async def test_without_message(self, request_body_without_message):
        request_body_without_message.message = None
        with pytest.raises(NextStepException):
            MessageService(request_body=request_body_without_message)

    async def test_edited_message(self, db, request_body_edited_message):
        handler = MessageService(request_body=request_body_edited_message)
        assert handler.has_edited_message is True

    async def test_message_is_edited(self, request_body_edited_message):
        message = MessageService(request_body=request_body_edited_message).get_message()
        assert message == request_body_edited_message.edited_message

    async def test_message(self, request_body_message):
        message = MessageService(request_body=request_body_message).get_message()
        assert message == request_body_message.message

    async def test_init_instance(self, db, request_body_message):
        message_service = MessageService(request_body=request_body_message)
        member_service = MemberService(db=db, message=message_service.message)
        await member_service.process()

        assert member_service.chat == await Chat.async_first(db=db, select_in_load=Chat.members)
        assert member_service.member == await Member.async_first(db=db)
        assert member_service.message == request_body_message.message
        chat_member_m2m = await ChatToMember.async_first(db=db, where=Chat.id == member_service.chat.id)

        assert chat_member_m2m.member.id == member_service.member.id
        assert chat_member_m2m.chat.id == member_service.chat.id

    async def test_bind_member(self, db, member_service):
        chat_member_m2m_before = await ChatToMember.async_first(db=db, where=ChatToMember.id == member_service.chat.id)
        chat_member_m2m_before.updated_at = datetime.datetime.now()
        chat_to_member = await ChatToMember.async_add(db, chat_member_m2m_before)
        before_datetime = chat_to_member.updated_at

        await member_service.process()
        chat_member_m2m_after = await ChatToMember.async_first(db=db, where=ChatToMember.id == member_service.chat.id)
        after_datetime = chat_member_m2m_after.updated_at

        assert chat_member_m2m_after.id == chat_member_m2m_before.id
        assert chat_member_m2m_after.chat.id == chat_member_m2m_before.chat.id
        assert before_datetime != after_datetime
