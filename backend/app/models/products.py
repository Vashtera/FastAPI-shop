from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, DECIMAL, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
from ..models.categories import Category

class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    image_url: Mapped[str] = mapped_column(String)

    category: Mapped["Category"] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"