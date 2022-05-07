import random
from typing import List

from bread_bot.telegramer.models import Member, Chat, ChatToMember
from bread_bot.telegramer.schemas.telegram_messages import MemberSchema
from bread_bot.telegramer.utils import structs


class MemberServiceMixin:
    @staticmethod
    async def get_username(member: MemberSchema) -> str:
        user_name = ''
        if member.first_name != '' or member.last_name != '':
            user_name = f'{member.first_name.strip()} ' \
                        f'{member.last_name.strip()}'

        if user_name.strip().replace('ㅤ', '') == '':
            user_name = f'@{member.username.capitalize()}'
        return user_name.strip()

    async def get_members(self) -> List[MemberSchema]:
        response = await self.client.get_chat(self.chat_id)
        chats = response.result
        chat_to_members = await ChatToMember.async_filter(
            db=self.db,
            where=ChatToMember.chat_id == self.chat_db.id,
            select_in_load=ChatToMember.member)
        result = [chat.user for chat in chats if not chat.user.is_bot]
        for chat_to_member in chat_to_members:
            member = MemberSchema.from_orm(chat_to_member.member)
            if member in result:
                continue
            result.append(member)
        return result

    async def get_one_of_group(self) -> str:
        if self.chat_id > 0:
            member = self.message.source
        else:
            member = random.choice(await self.get_members())
        return await self.get_username(member)

    async def who_is(self) -> str:
        params = self.params.replace('?', '')
        username = await self.get_one_of_group()
        return f'{random.choice(structs.DEFAULT_PREFIX)} ' \
               f'{params} {username}'

    async def gey_double(self) -> str:
        members = await self.get_members()
        random.shuffle(members)
        return f'Гей-парочку образовали: ' \
               f'{await self.get_username(members[0])} ' \
               f'и {await self.get_username(members[1])}'

    async def top(self) -> str:
        if self.chat_id > 0:
            members = [self.message.source]
        else:
            members = await self.get_members()
        result = ''
        i = 1
        random.shuffle(members)
        for user in members[:10]:
            if not user:
                continue
            result += f'{i}) {await self.get_username(user)}\n'
            i += 1
        return f'Топ {self.params}:\n{result}'

    async def handle_member(self, member: MemberSchema) -> Member:
        member_db = await Member.async_first(
            db=self.db,
            where=Member.username == member.username
        )
        if member_db is None:
            member_db: Member = await Member.async_add_by_kwargs(
                db=self.db,
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name,
                is_bot=member.is_bot,
            )
        else:
            is_updated = False
            if member.id != member_db.member_id:
                member_db.member_id = member.id
                is_updated = True
            for key in ('username', 'first_name', 'last_name'):
                if getattr(member, key, None) != getattr(member_db, key, None):
                    setattr(member_db, key, getattr(member, key))
                    is_updated = True
            if is_updated:
                member_db: Member = await Member.async_add(
                    db=self.db,
                    instance=member_db,
                )
        return member_db
