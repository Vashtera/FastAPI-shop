from fastapi import FastAPI 
from routers.users import router as users_router

app = FastAPI()

app.include_router(users_router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI-Shop"}