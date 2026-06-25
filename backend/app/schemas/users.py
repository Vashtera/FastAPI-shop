from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr


class UserBase(BaseModel):
    """
    Базовая схема пользователя.
    Содержит общие поля которые используются в других схемах.
    """

    first_name: str = Field(..., min_length=2, description="Имя пользователя, минимум 2 символа")
    last_name: str = Field(..., min_length=2, description="Фамилия пользователя, минимум 2 символа")
    email: EmailStr = Field(..., description="Email пользователя")
    login: str = Field(..., min_length=5, description="Логин пользователя, минимум 5 символов")


class UserCreate(UserBase):
    """
    Схема для создания нового пользователя.
    Наследует поля от UserBase и добавляет поле пароля.
    Используется при регистрации.
    """
    
    password: str = Field(..., description="Введите свой пароль от 8 символов")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:

        """Проверяет что пароль содержит минимум 8 символов."""

        if len(value) < 8:
            raise ValueError("Слишком короткий пароль, минимум 8 символов")
        return value
    

class UserResponse(UserBase):
    """
    Схема ответа API для пользователя.
    Наследует поля от UserBase и добавляет id.
    Не содержит пароль — безопасно возвращать клиенту.
    """

    id: int = Field(description="Уникальный идентификатор пользователя")

    model_config = ConfigDict(
        from_attributes=True,  # позволяет создавать схему из SQLAlchemy объекта
    )