from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
from ..models.products import Products

class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)

    products: Mapped["Products"] = relationship(back_populates="categories")

    def __repr__(self) -> str:
        return f"<Categories(id={self.id}, name='{self.name}')>"
