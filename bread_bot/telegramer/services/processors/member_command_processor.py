import random
from collections import defaultdict
from typing import List, Optional

from bread_bot.telegramer.clients.telegram_client import TelegramClient
from bread_bot.telegramer.models import ChatToMember, Stats
from bread_bot.telegramer.schemas.bread_bot_answers import TextAnswerSchema
from bread_bot.telegramer.schemas.telegram_messages import MemberSchema
from bread_bot.telegramer.services.processors.base_command_processor import CommandMessageProcessor
from bread_bot.telegramer.utils.structs import StatsEnum


class MemberCommandMessageProcessor(CommandMessageProcessor):
    METHODS_MAP = {
        "топ": "top",
        "top": "top",
        "кто": "who_is",
        "парочка": "get_love_couple",
        "стата": "show_stats",
        "статистика": "show_stats",
    }

    @staticmethod
    async def get_username(member: MemberSchema) -> str:
        user_name = ""
        if member.first_name != '' or member.last_name != '':
            user_name = f"{member.first_name.strip()} {member.last_name.strip()}"

        if user_name.strip().replace('ㅤ', '') == '':
            user_name = f"@{member.username.capitalize()}"
        return user_name.strip()

    async def get_members(self) -> List[MemberSchema]:
        response = await TelegramClient().get_chat(self.chat.chat_id)
        chat_to_members = await ChatToMember.async_filter(
            db=self.db,
            where=ChatToMember.chat_id == self.chat.id,
            select_in_load=ChatToMember.member)
        result = {}
        for chat in response.result:
            if chat.user.is_bot:
                continue
            result[chat.user.id] = chat.user
        for chat_to_member in chat_to_members:
            if chat_to_member.member and not chat_to_member.member.is_bot:
                member = chat_to_member.member
                if member.member_id in result.keys():
                    continue
                member_schema = MemberSchema(
                    is_bot=member.is_bot,
                    username=member.username,
                    first_name=member.first_name,
                    last_name=member.last_name,
                    id=member.member_id,
                )
                result[member_schema.id] = member_schema

        return list(result.values())

    async def get_one_of_group(self) -> str:
        if self.chat.chat_id > 0:
            member = self.message.source
        else:
            member = random.choice(await self.get_members())
        return await self.get_username(member)

    async def who_is(self) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.CALLED_WHO)
        params = self.command_params.replace('?', '')
        username = await self.get_one_of_group()
        return await self.get_text_answer(
            answer_text=f"{params} - это {username}"
        )

    async def get_love_couple(self) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.CALLED_WHO)
        members = await self.get_members()
        random.shuffle(members)
        return await self.get_text_answer(
            answer_text=f"Любовную парочку образовали: "
                        f"{await self.get_username(members[0])} и {await self.get_username(members[1])}"
        )

    async def top(self) -> Optional[TextAnswerSchema]:
        await self.count_stats(stats_enum=StatsEnum.CALLED_TOP)
        if self.chat.chat_id > 0:
            members = [self.message.source]
        else:
            members = await self.get_members()
        result = ""
        i = 1
        random.shuffle(members)
        if len(members) > 20:
            members = members[:20]
        for user in members:
            if not user:
                continue
            result += f"{i}) {await self.get_username(user)}\n"
            i += 1
        return await self.get_text_answer(
            answer_text=f"Топ {self.command_params}:\n{result}"
        )

    async def show_stats(self) -> Optional[TextAnswerSchema]:
        statistics = defaultdict(str)
        for stat in await Stats.async_filter(
                db=self.db,
                where=Stats.chat_id == self.chat.chat_id,
                select_in_load=Stats.member,
                order_by=Stats.count.desc()
        ):
            member = MemberSchema(
                first_name=stat.member.first_name,
                last_name=stat.member.last_name,
                username=stat.member.username,
                is_bot=stat.member.is_bot,
            )
            row = f"{await self.get_username(member)} - {stat.count}"
            if statistics[stat.slug] == "":
                statistics[stat.slug] = row + "\n"
            else:
                statistics[stat.slug] += row + "\n"
        result = ""
        for stat_slug, value in statistics.items():
            result += f"{StatsEnum[stat_slug].value}:\n{value}\n\n"
        return await self.get_text_answer(answer_text=result if result != "" else "Пока не набрал статистики")
