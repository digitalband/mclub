from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import SignUpSchema
from repositories.user import UserRepository

class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session=session)

    async def create_user(self, signup_data: SignUpSchema, role: str = "User") -> bool:
        user_created = await self.user_repo.create_user(signup_data, role=role)        
        return user_created is not None

    async def get_user_by_id(self, id: int) -> User | None:
        return await self.user_repo.get_user(id=id)
    
    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_user(email=email)
