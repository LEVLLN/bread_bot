import random

from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.common.exceptions.base import NextStepException, RaiseUpException
from bread_bot.common.models import (
    AnswerPack,
)
from bread_bot.common.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.common.services.handlers.command_methods.base_command_method import (
    COMMAND_INSTANCE_TYPE,
    BaseCommandMethod,
)
from bread_bot.common.services.member_service import ExternalMemberService, MemberService
from bread_bot.common.services.messages.message_service import MessageService
from bread_bot.common.utils.structs import (
    MemberCommandsEnum,
)


class MemberCommandMethod(BaseCommandMethod):
    def __init__(
        self,
        db: AsyncSession,
        command_instance: COMMAND_INSTANCE_TYPE,
        message_service: MessageService,
        member_service: MemberService,
        default_answer_pack: AnswerPack | None = None,
    ):
        super().__init__(db, command_instance, message_service, member_service, default_answer_pack)
        self.external_member_service = ExternalMemberService(
            db=self.db,
            message_service=self.message_service,
            member_service=self.member_service,
        )

    async def execute(self) -> TextAnswerSchema:
        match self.command_instance.command:
            case MemberCommandsEnum.WHO:
                return await self.get_who()
            case MemberCommandsEnum.TOP:
                return await self.get_top()
            case MemberCommandsEnum.COUPLE:
                return await self.get_couple()
            case MemberCommandsEnum.CHANNEL:
                return await self.get_channel()
            case _:
                raise NextStepException("Не найдена команда")

    async def get_who(self):
        rest_text = self.command_instance.rest_text.replace("?", "")
        username = await self.external_member_service.get_one_of_group()

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
        members = await self.external_member_service.get_members()
        rating = ""
        random.shuffle(members)
        if len(members) > 20:
            members = members[:20]
        for i, user in enumerate(members, 1):
            if not user:
                continue
            rating += f"{i}) {self.external_member_service.get_username(user)}\n"
        return super()._return_answer(f"Топ {self.command_instance.rest_text}\n{rating}")

    async def get_couple(self):
        members = await self.external_member_service.get_members()
        random.shuffle(members)
        if len(members) < 2:
            raise RaiseUpException("В группе недостаточно пользователей для образования пары!")
        return super()._return_answer(
            f"Парочку {self.command_instance.rest_text} образовали: "
            f"{self.external_member_service.get_username(members[0])} "
            f"и {self.external_member_service.get_username(members[1])}"
        )

    async def get_channel(self):
        members = await self.external_member_service.get_members()
        return super()._return_answer(" ".join([f"@{member.username}" for member in members]))
