from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.products import Product
from ..schemas.products import ProductCreate


class ProductRepo():
    def __init__(self, session: AsyncSession):
        self.session = session

    