import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.session import Session

log = logging.getLogger(__name__)


class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self, user_id: int, session_id: str, refresh_token: str, expires_at: int | timedelta
    ) -> str | None:
        now = datetime.now(timezone.utc)

        if isinstance(expires_at, int):
            expire = now + timedelta(minutes=expires_at)
        elif isinstance(expires_at, timedelta):
            expire = now + expires_at

        auth_session = Session(
            user_id=user_id,
            id=session_id,
            refresh_token=refresh_token,
            expires_at=expire
        )
        try:
            self.session.add(auth_session)
            await self.session.commit()
            return auth_session.id
        except Exception as e:
            log.error("DB Failed create session > %s", e)