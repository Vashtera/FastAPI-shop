from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import User
from ..schemas.users import UserCreate


class UserRepo:
    """
    Репозиторий для работы с таблицей users.
    Содержит все запросы к БД связанные с пользователями.
    """

    def __init__(self, session: AsyncSession):
        """
        Args:
            session: асинхронная сессия SQLAlchemy
        """
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID.

        Args:
            user_id: уникальный идентификатор пользователя

        Returns:
            Объект User или None 
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email

        Args:
            email: email адрес пользователя

        Returns:
            Объект User или None
        """
        result = await self.session.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        from app.core.security import hash_password
        data = user_data.model_dump()
        data["hashed_password"] = hash_password(data.pop("password"))
        """
        Создать нового пользователя в БД.

        Args:
            user_data: валидированные данные пользователя

        Returns:
            Созданный объект User с присвоенным id

        Raises:
            Exception: при ошибке создания откатывает транзакцию
        """
        try:
            db_user = User(**data)
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user
        except Exception as e:
            await self.session.rollback()
            raise e