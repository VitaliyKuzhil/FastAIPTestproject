# Залежності (наприклад, перевірка чи існує категорія)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.category.service import CategoryService

def get_category_service(session: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(session=session)