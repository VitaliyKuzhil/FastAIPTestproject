# Бізнес-логіка (робота з БД)
from typing import List, Optional, Tuple, Dict
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


from src.database import get_db
from src.category.models import Category
from src.category.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from src.category.constants import CategoryStatus
from src.category.exceptions import CategoryNotFoundException, InvalidParentCategoryException


class CategoryService:
    # 4. Підключення ін'єкції залежностей у __init__
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    # 3. Проблема N+1 запитів та захист від зациклення (A -> B -> A)
    async def build_full_path(self, category: Category, cat_map: Optional[Dict[int, Category]] = None) -> str:
        """Рекурсивно будує повний шлях категорії.
        Якщо передано cat_map, будує шлях у пам'яті (оптимізація N+1)."""
        path_parts = []
        current = category
        visited = set()

        while current:
            # Захист від нескінченного циклу при некоректних даних у БД
            if current.category_id in visited:
                break
            visited.add(current.category_id)

            path_parts.insert(0, current.name)

            if current.parent_category_id:
                if cat_map is not None:
                    # Оптимізований пошук у пам'яті
                    current = cat_map.get(current.parent_category_id)
                else:
                    # Пошук у БД (для поодиноких запитів, як GET по ID)
                    parent_result = await self.session.execute(
                        select(Category).where(Category.category_id == current.parent_category_id)
                    )
                    current = parent_result.scalar_one_or_none()
            else:
                break

        return " > ".join(path_parts)

    # 2. Неузгодженість типу повернення у create_category
    async def create_category(self, schema: CategoryCreate) -> CategoryResponse:
        """Створення категорії з перевіркою parent_category_id."""
        if schema.parent_category_id and schema.parent_category_id > 0:
            parent = await self.session.get(Category, schema.parent_category_id)
            if not parent:
                raise CategoryNotFoundException(schema.parent_category_id)
        else:
            schema.parent_category_id = None

        category_data = schema.model_dump()
        category = Category(**category_data)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)

        # Повертаємо CategoryResponse із розрахованим full_path
        full_path = await self.build_full_path(category)
        response = CategoryResponse.model_validate(category)
        response.full_path = full_path
        return response

    async def get_category_by_id(self, category_id: int) -> CategoryResponse:
        """Отримання однієї категорії з повним шляхом."""
        category = await self.session.get(Category, category_id)
        if not category:
            raise CategoryNotFoundException(category_id)

        full_path = await self.build_full_path(category)

        response_data = CategoryResponse.model_validate(category)
        response_data.full_path = full_path
        return response_data

    async def get_categories_list(
            self,
            search_id: Optional[int] = None,
            search_name: Optional[str] = None,
            status: Optional[CategoryStatus] = None,
            sort_order: str = "asc",
            page: int = 1,
            page_size: int = 20
    ) -> Tuple[List[CategoryResponse], int]:
        """Вибірка списку категорій із фільтрацією, пошуком, сортуванням за повним шляхом та пагінацією."""

        # 3. Витягуємо всі категорії одним запитом для побудови дерева в пам'яті (захист від N+1)
        all_categories_result = await self.session.execute(select(Category))
        all_categories = all_categories_result.scalars().all()
        cat_map = {c.category_id: c for c in all_categories}

        query = select(Category)

        # Фільтрація
        if search_id is not None:
            query = query.where(Category.category_id == search_id)
        if search_name:
            query = query.where(Category.name.ilike(f"%{search_name}%"))

        # 1. Прихований баг із фільтрацією за статусом (якщо статус == 0)
        if status is not None:
            query = query.where(Category.status == status)

        # Отримання загальної кількості для пагінації
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.session.execute(count_query)).scalar_one()

        # Виконуємо запит
        result = await self.session.execute(query)
        categories = result.scalars().all()

        # Формуємо список з повними шляхами через словник cat_map
        category_responses: List[CategoryResponse] = []
        for cat in categories:
            full_path = await self.build_full_path(cat, cat_map=cat_map)
            res = CategoryResponse.model_validate(cat)
            res.full_path = full_path
            category_responses.append(res)

        # Сортування за повним шляхом або ID
        reverse = sort_order.lower() == "desc"
        category_responses.sort(key=lambda x: (x.full_path or "", x.category_id), reverse=reverse)

        # Пагінація на рівні зрізу в пам'яті (оскільки ми сортуємо за розрахованим full_path)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_items = category_responses[start:end]

        return paginated_items, total_count

    async def update_category(self, category_id: int, schema: CategoryUpdate) -> CategoryResponse:
        """Оновлення категорії."""
        category = await self.session.get(Category, category_id)
        if not category:
            raise CategoryNotFoundException(category_id)

        update_data = schema.model_dump(exclude_unset=True)

        # Захист від призначення категорії самої себе батьківською
        if "parent_category_id" in update_data:
            parent_id = update_data["parent_category_id"]
            if parent_id == category_id:
                raise InvalidParentCategoryException()
            if parent_id and parent_id > 0:
                parent = await self.session.get(Category, parent_id)
                if not parent:
                    raise CategoryNotFoundException(parent_id)
            else:
                update_data["parent_category_id"] = None

        for key, value in update_data.items():
            setattr(category, key, value)

        await self.session.commit()
        await self.session.refresh(category)

        full_path = await self.build_full_path(category)
        response = CategoryResponse.model_validate(category)
        response.full_path = full_path
        return response

    async def delete_category(self, category_id: int) -> None:
        """Видалення категорії (підкатегорії видаляються рекурсивно через CASCADE у моделі)."""
        category = await self.session.get(Category, category_id)
        if not category:
            raise CategoryNotFoundException(category_id)

        await self.session.delete(category)
        await self.session.commit()
