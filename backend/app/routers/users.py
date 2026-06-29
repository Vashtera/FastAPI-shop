from typing import Annotated
from ..core.security import (
    hash_password, verify_password, create_access_token, verify_access_token
)
from ..services.auth import register
from ..schemas.users import UserCreate
from fastapi import Depends, APIRouter, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()
router = APIRouter()

def get_session()


@router.post("/registration")
async def register(data: UserCreate, session: )