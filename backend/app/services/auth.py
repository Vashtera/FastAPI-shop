from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.users_repo import UserRepo
from ..schemas.users import UserCreate


async def register(user: UserCreate, db: AsyncSession):
    """
    Сервис регистрации нового пользователя.

    Проверяет уникальность email и создаёт нового пользователя в БД.

    Args:
        user: данные нового пользователя (валидированные через Pydantic)
        db: асинхронная сессия SQLAlchemy

    Returns:
        Созданный объект User

    Raises:
        HTTPException 400: если пользователь с таким email уже существует
    """
    repo = UserRepo(db)
    existing_user = await repo.get_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist",
        )
    return await repo.create_user(user)