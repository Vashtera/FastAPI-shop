from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ..schemas.categories import CategoryResponse

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Наименование товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: float = Field(..., gt=0, description="Цена товара(должна быть больше 0)")
    category_id: int = Field(..., description="ID категории")
    image_url: Optional[str] = Field(None, description="URL фотографии товара")


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int = Field(..., description="ID товава")
    created_at: datetime = Field(..., description="Время создания товара")
    category: CategoryResponse = Field(..., description="Категория товара")

    model_config = ConfigDict(
        from_attributes=True,  # позволяет создавать схему из SQLAlchemy объекта
    )

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int = Field(..., description="Количество товара")