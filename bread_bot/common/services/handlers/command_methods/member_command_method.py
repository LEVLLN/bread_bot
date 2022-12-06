import asyncio
import random

from sqlalchemy import and_

from bread_bot.common.clients.telegram_client import TelegramClient
from bread_bot.common.exceptions.base import NextStepException, RaiseUpException
from bread_bot.common.models import (
    ChatToMember,
    Member,
)
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.schemas.telegram_messages import MemberSchema
from bread_bot.common.services.handlers.command_methods.base_command_method import BaseCommandMethod
from bread_bot.common.utils.structs import (
    MemberCommandsEnum,
)


class MemberCommandMethod(BaseCommandMethod):
    async def execute(self) -> TextAnswerSchema:
        match self.command_instance.command:
            case MemberCommandsEnum.WHO:
                return await self.get_who()
            case MemberCommandsEnum.TOP:
                return await self.get_top()
            case MemberCommandsEnum.COUPLE:
                return await self.get_couple()
            case _:
                raise NextStepException("Не найдена команда")

    @staticmethod
    def get_username(member: MemberSchema) -> str:
        user_name = ""
        if member.first_name != "" or member.last_name != "":
            user_name = f"{member.first_name.strip()} {member.last_name.strip()}"
        return user_name.strip()

    async def _get_chat_members(self) -> dict:
        """Получение из сохраненных members из БД"""
        result = {}
        chat_to_members = await ChatToMember.async_filter(
            db=self.db,
            where=and_(
                ChatToMember.chat_id == self.member_service.chat.id,
                Member.is_bot == False,
                Member.id is not None,
                Member.username is not None,
            ),
            select_in_load=ChatToMember.member,
        )
        for chat_to_member in chat_to_members:
            if chat_to_member.member and not chat_to_member.member.is_bot:
                member = chat_to_member.member
                member_schema = MemberSchema(
                    is_bot=member.is_bot,
                    username=member.username,
                    first_name=member.first_name,
                    last_name=member.last_name,
                    id=member.member_id,
                )
                result[member_schema.id] = member_schema
        return result

    async def _get_admin_members(self) -> dict:
        """Получение администраторов группы"""
        response = await TelegramClient().get_chat(self.member_service.chat.chat_id)
        result = {}
        for chat in response.result:
            if chat.user.is_bot:
                continue
            if chat.user.id is None:
                continue
            if chat.user.username is None:
                continue
            result[chat.user.id] = chat.user
        return result

    async def get_members(self) -> list[MemberSchema]:
        """Получить пользователей чата"""
        if self.member_service.chat.chat_id > 0:
            return [
                self.message_service.message.source,
            ]
        admin_members, members = await asyncio.gather(
            self._get_chat_members(),
            self._get_admin_members(),
        )
        return list({**admin_members, **members}.values())

    async def get_one_of_group(self) -> str:
        """Получение случайного пользователя из группы"""
        member = random.choice(await self.get_members())
        return self.get_username(member)

    async def get_who(self):
        rest_text = self.command_instance.rest_text.replace("?", "")
        username = await self.get_one_of_group()

        match self.command_instance.raw_command.lower():
            case "кто":
                answer_text = f"{username} {rest_text}"
            case "у кого":
                answer_text = f"{rest_text} у {username}"
            case "кем":
                answer_text = f"{rest_text} им: {username}"
            case "с кем":
                answer_text = f"{rest_text} с {username}"
            case "кого":
                answer_text = f"{rest_text} {username}"
            case "кому":
                answer_text = f"{rest_text} ему: {username}"
            case "о ком":
                answer_text = f"{rest_text} о {username}"
            case "чья" | "чьё" | "чей" | "чье":
                answer_text = f"{rest_text} его: {username}"
            case _:
                answer_text = f"{rest_text} - это {username}"
        return super()._return_answer(answer_text)

    async def get_top(self):
        members = await self.get_members()
        rating = ""
        random.shuffle(members)
        if len(members) > 20:
            members = members[:20]
        for i, user in enumerate(members, 1):
            if not user:
                continue
            rating += f"{i}) {self.get_username(user)}\n"
        return super()._return_answer(f"Топ {self.command_instance.rest_text}\n{rating}")

    async def get_couple(self):
        members = await self.get_members()
        random.shuffle(members)
        if len(members) < 2:
            raise RaiseUpException("В группе недостаточно пользователей для образования пары!")
        return super()._return_answer(
            f"Парочку {self.command_instance.rest_text} образовали: "
            f"{self.get_username(members[0])} и {self.get_username(members[1])}"
        )
