from ..core.security import (
    hash_password, verify_password, create_access_token, verify_access_token
)
from ..services.auth import register
from ..schemas.users import UserCreate
from fastapi import Depends, APIRouter, FastAPI
from ..services.dependencies import get_session

app = FastAPI()
router = APIRouter()


@router.post("/registration")
async def registration(user: UserCreate, session =  Depends(get_session)):
    return await register(user, session)