import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.session import Session
from schemas.auth import SessionSchema

log = logging.getLogger(__name__)


class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(self, session: SessionSchema) -> str | None:
        auth_session = Session(**session)
        try:
            self.session.add(auth_session)
            await self.session.commit()
            return auth_session.id
        except Exception as e:
            log.error("DB Failed create session > %s", e)

    async def update_session(
        self, session: Session, refresh_token: str, expires_at: datetime
    ) -> str | None:
        try:
            session.refresh_token = refresh_token
            session.expires_at = expires_at
            await self.session.commit()
            return session.id
        except Exception as e:
            log.error("DB Failed update session > %s", e)
        
    async def get_session_by_id(self, session_id: str) -> Session | None:
        return await self.get_session(id=session_id)
    
    async def get_session(self, **filter) -> Session | None:
        query = select(Session).filter_by(**filter).limit(1)
        user = await self.session.execute(query)
        return user.scalar_one_or_none()
    
    async def delete_session(self, session: Session) -> bool:
        try:
            await self.session.delete(session)
            await self.session.commit()
            return True
        except Exception as e:
            log.error("DB Failed delete session > %s", e)
            return False