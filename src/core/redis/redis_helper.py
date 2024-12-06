import logging

import redis.asyncio as redis

from core.config import settings


log = logging.getLogger(__name__)


class RedisHelper:
    def __init__(self, host: str, port: int, db: int, password: str) -> None:
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)

    async def add_verification_code(self, email: str, value: str, expiration: int) -> bool:
        try:
            key = f"verification_code:{email}"
            return await self.redis.set(name=key, value=value, ex=expiration)
        except Exception as e:
            log.error(
            "Failed add_verification_code to Redis email > %s, value > %s, error_message > %s", 
            email, value, e
           )
        
        return False

    async def get_verification_code(self, email: str) -> str | None:
        try:
            key = f"verification_code:{email}"
            return await self.redis.get(key)
        except Exception as e:
            log.error(
                "Failed get_verification_code from Redis email > %s, error_message > %s",
                email, e
            )

    async def delete_verification_code(self, email: str) -> bool:
        try:
            key = f"verification_code:{email}"
            return bool(await self.redis.delete(key))
        except Exception as e:
            log.error(
                "Failed delete_verification_code from Redis email > %s, error_message > %s",
                email, e
            )
        return False

    async def session_in_black_list(self, session_id: str) -> bool:
        try:
            key = f"jid_black_list:{session_id}"
            return bool(await self.redis.get(key))
        except Exception as e:
            log.error(
                "Failed token_in_black_list from Redis session_id > %s, error_message > %s",
                session_id, e
            )
        return False

    async def add_session_in_black_list(self, session_id: str, expiration: int) -> bool:
        try:
            key = f"jid_black_list:{session_id}"
            return await self.redis.set(name=key, value="signout", ex=expiration)
        except Exception as e:
            log.error(
                "Failed add_token_in_black_list from Redis session_id > %s, error_message > %s",
                session_id, e
            )
        return False

redis_helper = RedisHelper(
    host=settings.redis.REDIS_HOST, 
    port=settings.redis.REDIS_PORT,
    db=settings.redis.REDIS_DB,
    password=settings.redis.REDIS_PASS
)
