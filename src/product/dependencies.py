# Залежності (наприклад, перевірка чи існує продукт)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.product.service import ProductService

def get_product_service(session: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(session=session)