from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from core.security import oauth2_scheme, verify_access_token
from repositories.users_repo import UserRepo



async def get_session():
    async with SessionLocal() as session:
        yield session


async def get_current_user(
        user = UserRepo,
        token: str = Depends(oauth2_scheme)
        ):
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
