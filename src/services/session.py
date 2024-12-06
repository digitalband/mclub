import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.session import SessionRepository
from models.session import Session


class SessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session_repo = SessionRepository(session=session)

    async def create_session(
        self, user_id: int, session_id: str, refresh_token: str, expires_at: datetime
    ) -> str | None:
        return await self.session_repo.create_session(user_id=user_id, session_id=session_id, refresh_token=refresh_token, expires_at=expires_at)

    async def update_session(
        self, session: Session, refresh_token: str, expires_at: datetime
    ) -> str | None:
        return await self.session_repo.update_session(session=session, refresh_token=refresh_token, expires_at=expires_at)

    async def get_session_by_id(self, session_id: str) -> Session | None:
        return await self.session_repo.get_session(id=session_id)
    
    async def delete_session(self, session_id: str) -> bool:
        session = await self.get_session_by_id(session_id)
        if session:
            return await self.session_repo.delete_session(session)
        return False