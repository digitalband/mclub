
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

log = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user(self, **filter) -> User | None:
        query = select(User).filter_by(**filter).limit(1)
        user = await self.session.execute(query)
        return user.scalar_one_or_none()
    
    async def create_user(self, signup_data, role: str) -> int | None:
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