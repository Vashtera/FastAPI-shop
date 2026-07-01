from pydantic import BaseModel, Field, ConfigDict

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Наименование категории")
    slug: str = Field(..., min_length=2, max_length=100, description="URL категории")


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int = Field(..., description="id категории")

    model_config = ConfigDict(
        from_attributes=True,  # позволяет создавать схему из SQLAlchemy объекта
    )