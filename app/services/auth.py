import secrets
import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from services.base import BaseService
from database import async_session_maker
from models.token import RefreshToken


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

class RefreshTokenService(BaseService):
    model = RefreshToken

    @classmethod
    async def create_and_save_refresh_token(cls, user_id: int, expires_days: int = 7) -> str:
        raw_token = secrets.token_urlsafe(32)
        hashed = hash_token(raw_token)
        
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=expires_days)

        async with async_session_maker() as session:
            async with session.begin():
                await session.execute(
                    delete(RefreshToken).where(RefreshToken.user_id == user_id)
                )

                db_token = RefreshToken(
                    user_id=user_id,
                    token=hashed,
                    expires_at=expires_at,
                    created_at=now
                )
                session.add(db_token)
        
        return raw_token

    @classmethod
    async def rotate_refresh_token(cls, raw_token: str, expires_days: int = 7) -> tuple[str, int]:

        hashed = hash_token(raw_token)
        now = datetime.now(timezone.utc)

        async with async_session_maker() as session:
            async with session.begin():
                query = select(RefreshToken).where(RefreshToken.token == hashed)
                result = await session.execute(query)
                db_refresh = result.scalar_one_or_none()

                if not db_refresh:
                    return None, None

                user_id = db_refresh.user_id

                db_expires = db_refresh.expires_at.replace(tzinfo=timezone.utc) if db_refresh.expires_at.tzinfo is None else db_refresh.expires_at
                if db_expires < now:
                    await session.delete(db_refresh)
                    return "expired", None

                await session.delete(db_refresh)

        new_raw_token = await cls.create_and_save_refresh_token(user_id=user_id, expires_days=expires_days)
        return new_raw_token, user_id

    @classmethod
    async def revoke_refresh_token(cls, raw_token: str) -> None:
        if not raw_token or not raw_token.strip():
            return False

        hashed = hash_token(raw_token)

        async with async_session_maker() as session:
            async with session.begin():
                query = delete(RefreshToken).where(RefreshToken.token == hashed)
                result = await session.execute(query)
                
                deleted_rows = result.rowcount
            
            if deleted_rows > 0:
                return True
        return False
