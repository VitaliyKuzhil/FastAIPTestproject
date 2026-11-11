# Ендпоінти (GET, POST, PATCH, DELETE)
from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, status

from src.category.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse
)
from src.category.constants import CategoryStatus
from src.category.service import CategoryService

router = APIRouter(
    prefix="/category",
    tags=["Category"]
)

@router.get("", response_model=CategoryListResponse)
async def get_categories(
    search_id: Optional[int] = Query(None, description="Пошук за ID"),
    search_name: Optional[str] = Query(None, description="Пошук за назвою"),
    status: Optional[CategoryStatus] = Query(None, description="Фільтр за статусом (1 - Включена, 0 - Виключена)"),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Сортування: asc (від А до Я) або desc (від Я до А)"),
    page: int = Query(1, ge=1, description="Номер сторінки"),
    page_size: int = Query(20, ge=1, le=100, description="Кількість записів на сторінку"),
    service: CategoryService = Depends(CategoryService)
):
    """
    Повертає список категорій із пагінацією, фільтрацією та сортуванням за повним шляхом.
    """
    items, total = await service.get_categories_list(
        search_id=search_id,
        search_name=search_name,
        status=status,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    return CategoryListResponse(items=items, total=total)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    service: CategoryService = Depends(CategoryService)
):
    """
    Повертає всі дані про категорію за її ID.
    """
    return await service.get_category_by_id(category_id)

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    schema: CategoryCreate,
    service: CategoryService = Depends(CategoryService)
):
    """
    Створення нової категорії.
    Якщо parent_category_id не передано або дорівнює 0 — це головна категорія.
    """
    return await service.create_category(schema)

@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    schema: CategoryUpdate,
    service: CategoryService = Depends(CategoryService)
):
    """
    Редагування категорії. Поля date_added, date_modify та category_id редагувати не можна.
    """
    return await service.update_category(category_id, schema)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(CategoryService)
):
    """
    Видалення категорії. Усі підкатегорії видаляються рекурсивно.
    """
    await service.delete_category(category_id)
