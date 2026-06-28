from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.users import UserCreate
from ..repositories.users_repo import UserRepo


async def register(user: UserCreate, db: AsyncSession):
    repo = UserRepo(db)
    existing_user = repo.get_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    return await repo.create_user(existing_user)

