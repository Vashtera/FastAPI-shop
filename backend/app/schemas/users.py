from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    email: EmailStr
    login: str = Field(..., min_length=5)

    
class UserCreate(UserBase):
    password: str = Field(..., description="Введите свой пароль от 8 символов")

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Слишком короткий пароль")
        return value 
    

class UserResponse(UserBase):
    id: int = Field(...)

    model_config = ConfigDict(from_attributes=True)