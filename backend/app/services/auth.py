from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.users import UserCreate, UserResponse
from ..repositories.users_repo import UserRepo
from database import get_db


async def register(user: UserCreate, db: AsyncSession) -> UserResponse:
    existing_user = UserRepo.get_by_email(user)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )