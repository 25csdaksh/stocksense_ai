"""
User & Authentication Repository.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.db.models.user import User
from app.core.security import hash_password


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username.strip())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.strip().lower())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False
    ) -> User:
        hashed_pw = hash_password(password)
        return await self.create(
            username=username.strip(),
            email=email.strip().lower(),
            hashed_password=hashed_pw,
            full_name=full_name,
            is_superuser=is_superuser,
            is_active=True
        )
