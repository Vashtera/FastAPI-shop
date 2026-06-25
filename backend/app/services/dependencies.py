from jose import JWTError, jwt
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from ..schemas.users import UserBase
from ..repositories.users_repo import UserRepo


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserBase:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: Optional[str] = payload.get("sub")
        if login is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = await UserRepo.get_by_login(login)
    if not user:
        raise cred_exc
    return UserBase(login=user["username"], full_name=user.get("full_name"))