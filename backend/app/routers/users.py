from ..core.security import (
    hash_password, verify_password, create_access_token, verify_access_token
)
from ..services.auth import register
from fastapi import Depends, APIRouter, FastAPI

app = FastAPI()
router = APIRouter()
