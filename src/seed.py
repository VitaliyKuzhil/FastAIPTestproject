import asyncio
from decimal import Decimal
from sqlalchemy import select

from src.database import async_session_maker
from src.category.models import Category
from src.product.models import Product, ProductCategory, ProductImage, ProductAttribute, ProductStore

from src.manufacturer.models import Manufacturer
from src.store.models import Store


async def seed_data():
    async with async_session_maker() as session:
        # Перевірка наявних даних
        existing_cat = await session.execute(select(Category))
        if existing_cat.scalars().first():
            print("База даних вже містить дані. Пропуск сідування.")
            return

        print("Розпочинаємо заповнення демо-даними...")

        # 1. Виробники
        m1 = Manufacturer(name="Shoei", sort_order=1)
        m2 = Manufacturer(name="Alpinestars", sort_order=2)
        session.add_all([m1, m2])
        await session.flush()

        # 2. Магазини
        s1 = Store(name="Головний магазин (Київ)", url="https://store-kyiv.ua")
        s2 = Store(name="Онлайн магазин", url="https://store-online.ua")
        session.add_all([s1, s2])
        await session.flush()

        # 3. Дерево категорій (3 рівні вкладеності)
        cat_root = Category(name="Мотоекіпірування", status="1", parent_category_id=None)
        session.add(cat_root)
        await session.flush()

        cat_sub = Category(name="Шоломи", status="1", parent_category_id=cat_root.category_id)
        session.add(cat_sub)
        await session.flush()

        cat_child = Category(name="Інтеграли", status="1", parent_category_id=cat_sub.category_id)
        session.add(cat_child)
        await session.flush()

        # 4. Товари
        p1 = Product(
            name="Мотошолом Shoei NXR 2",
            description="Преміальний шолом для міської та трекової їзди з високим рівнем безпеки.",
            price=Decimal("18500.00"),
            model="NXR-2-BLK",
            manufacturer_id=m1.manufacturer_id,
            seo_keyword="shoei-nxr-2-black",
            meta_title="Купити шолом Shoei NXR 2",
            status="ACTIVE",
            rating=4.9,
            viewed=120
        )
        session.add(p1)
        await session.flush()

        # 5. Прив'язки товару (Категорії, Зображення, Атрибути, Магазини)
        session.add(ProductCategory(product_id=p1.product_id, category_id=cat_child.category_id))

        session.add_all([
            ProductImage(product_id=p1.product_id, image="shoei_nxr2_front.jpg", sort_order=1),
            ProductImage(product_id=p1.product_id, image="shoei_nxr2_side.jpg", sort_order=2)
        ])

        session.add_all([
            ProductAttribute(product_id=p1.product_id, group_name="Характеристики", name="Матеріал", value="Карбон / Скловолокно", sort_order=1),
            ProductAttribute(product_id=p1.product_id, group_name="Характеристики", name="Вага", value="1390 г", sort_order=2),
            ProductAttribute(product_id=p1.product_id, group_name="Сертифікація", name="Стандарт", value="ECE 22.06", sort_order=1)
        ])

        session.add_all([
            ProductStore(product_id=p1.product_id, store_id=s1.store_id),
            ProductStore(product_id=p1.product_id, store_id=s2.store_id)
        ])

        await session.commit()
        print("Демо-дані успішно додано!")

if __name__ == "__main__":
    asyncio.run(seed_data())