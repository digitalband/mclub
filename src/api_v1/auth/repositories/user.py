import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from api_v1.auth.schemas import SignUpSchema

log = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_user_by_id(self, id: int) -> User | None:
        return await self.__get_user(id=id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.__get_user(email=email)

    async def __get_user(self, **filter) -> User | None:
        query = select(User).filter_by(**filter).limit(1)
        user = await self.session.execute(query)
        return user.scalar_one_or_none()
    
    async def create_user(self, signup_data: SignUpSchema, role: str) -> int | None:
        user = User(
            **signup_data.model_dump(exclude_none=True),
            role=role
        )
        try:
            self.session.add(user)
            await self.session.commit()
            return user.id
        except Exception as e:
            log.error("DB Failed create user > %s", e)