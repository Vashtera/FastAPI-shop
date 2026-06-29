from ..core.security import create_access_token
from ..services.auth import register, authenticate_user
from ..schemas.users import UserCreate, UserResponse, Token
from fastapi import Depends, APIRouter, FastAPI, status, HTTPException
from ..services.dependencies import get_session
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()
router = APIRouter()


@router.post("/registration/", response_model=UserResponse)
async def registration(user: UserCreate, session =  Depends(get_session)):
    return await register(user, session)


@router.post("/login/", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
    ):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}