from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from core.db.db_helper import db_helper

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).filter_by(email=email).limit(1)
        user = await self.session.execute(query)
        return user.scalar_one_or_none()
