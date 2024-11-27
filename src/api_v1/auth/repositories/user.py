from sqlalchemy import select

from models.user import User
from core.db import db_helper

class UserRepository:
    def __init__(self) -> None:
        pass

    async def get_user_by_email(self, email: str) -> User | None:
        async with db_helper.session_factory() as session:
            query = select(User).filter_by(email=email).limit(1)
            user = await session.execute(query)
            return user.scalar_one_or_none()