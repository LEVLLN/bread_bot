from bread_bot.telegramer.models import Chat, Member, ChatToMember
from bread_bot.telegramer.services.message_service import MessageService


class TestMessageHandler:
    async def test_has_message(self, request_body_message):
        handler = MessageService(request_body=request_body_message)
        assert await handler.has_message is True

    async def test_without_message(self, request_body_without_message):
        request_body_without_message.message = None
        handler = MessageService(request_body=request_body_without_message)
        assert await handler.has_message is False

    async def test_edited_message(self, db, request_body_edited_message):
        handler = MessageService(request_body=request_body_edited_message)
        assert await handler.has_edited_message is True

    async def test_message_is_edited(self, request_body_edited_message):
        message = await MessageService(request_body=request_body_edited_message).get_message()
        assert message == request_body_edited_message.edited_message

    async def test_message(self, request_body_message):
        message = await MessageService(request_body=request_body_message).get_message()
        assert message == request_body_message.message

    async def test_init_instance(self, db, request_body_message):
        handler = MessageService(request_body=request_body_message, db=db)
        await handler.init()

        assert handler.chat == await Chat.async_first(db=db, select_in_load=Chat.members)
        assert handler.member == await Member.async_first(db=db)
        assert handler.message == request_body_message.message
        chat_member_m2m = await ChatToMember.async_first(db=db, where=Chat.id == handler.chat.id)

        assert chat_member_m2m.member.id == handler.member.id
        assert chat_member_m2m.chat.id == handler.chat.id
