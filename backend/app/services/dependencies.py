from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from ..core.security import oauth2_scheme, verify_access_token
from ..repositories.users_repo import UserRepo


async def get_session():
    """
    Зависимость для получения асинхронной сессии БД.
    Автоматически закрывает сессию после завершения запроса.

    Yields:
        Асинхронная сессия SQLAlchemy
    """
    async with SessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    """
    Зависимость для получения текущего авторизованного пользователя.
    Декодирует JWT токен и возвращает объект пользователя из БД.

    Args:
        token: JWT токен из заголовка Authorization
        session: асинхронная сессия БД (через Depends)

    Returns:
        Объект User текущего пользователя

    Raises:
        HTTPException 401: если токен невалидный или истёк
        HTTPException 401: если пользователь не найден в БД
    """
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UserRepo(session)
    user = await repo.get_by_id(user_id_int)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user