from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import verify_password
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


async def authenticate_user(email: str, password: str, db: AsyncSession):
    repo = UserRepo(db)
    user = await repo.get_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def give_seller_role_service(user_id: int, db: AsyncSession):
    repo = UserRepo(db)
    return await repo.give_seller_role_repo(user_id)


async def get_profile_user(user_id: int, db: AsyncSession):
    repo = UserRepo(db)
    return await repo.get_by_id(user_id)
