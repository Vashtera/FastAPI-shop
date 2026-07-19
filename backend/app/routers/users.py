from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import create_access_token
from ..schemas.users import Token, UserCreate, UserResponse
from ..services.auth import authenticate_user, register
from ..services.dependencies import get_session


router = APIRouter(
    prefix="/users", 
    tags=["users"]
)


@router.post("/registration/", response_model=UserResponse)
async def registration(user: UserCreate, session=Depends(get_session)):
    """
    Регистрация нового пользователя.

    Args:
        user: данные нового пользователя (валидированные через Pydantic)
        session: асинхронная сессия БД (через Depends)

    Returns:
        Созданный пользователь в формате UserResponse (без пароля)

    Raises:
        HTTPException 400: если пользователь с таким email уже существует
    """
    return await register(user, session)


@router.post("/login/", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """
    Авторизация пользователя и получение JWT токена.

    Args:
        form_data: данные формы логина (username и password)
        session: асинхронная сессия БД (через Depends)

    Returns:
        Словарь с access_token и token_type

    Raises:
        HTTPException 401: если логин или пароль неверные
    """
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}