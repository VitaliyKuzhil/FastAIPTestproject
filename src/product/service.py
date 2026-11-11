# Бізнес-логіка (робота з БД)
from typing import List, Optional, Tuple, Literal
from fastapi import Depends
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.product.models import Product, ProductCategory, ProductImage, ProductAttribute, ProductStore

from src.category.service import CategoryService
from src.product.schemas import (
    ProductCreate, ProductUpdate, ProductDetailResponse, ProductListItemResponse,
    ProductImageBase, ProductAttributeBase, ProductCategoryResponse, ProductStoreResponse
)
from src.product.exceptions import ProductNotFoundException, ProductSeoKeywordAlreadyExistsException
from fastapi import HTTPException, status


class ProductService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session
        self.category_service = CategoryService(session)

    async def _get_product_or_404(self, product_id: int) -> Product:
        result = await self.session.execute(
            select(Product)
            .options(
                selectinload(Product.categories).selectinload(ProductCategory.category),
                selectinload(Product.images),
                selectinload(Product.attributes),
                selectinload(Product.stores).selectinload(ProductStore.store),
                selectinload(Product.manufacturer)
            )
            .where(Product.product_id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise ProductNotFoundException(product_id)
        return product

    async def create_product(self, schema: ProductCreate) -> ProductDetailResponse:
        if schema.seo_keyword:
            existing = await self.session.execute(
                select(Product).where(Product.seo_keyword == schema.seo_keyword)
            )
            if existing.scalar_one_or_none():
                raise ProductSeoKeywordAlreadyExistsException(schema.seo_keyword)

        product_data = schema.model_dump(exclude={"category_ids", "images", "attributes", "store_ids"})
        product = Product(**product_data)
        self.session.add(product)
        await self.session.flush()

        # Додавання категорій
        for cat_id in schema.category_ids:
            self.session.add(ProductCategory(product_id=product.product_id, category_id=cat_id))

        # Додавання зображень
        for img in schema.images:
            self.session.add(ProductImage(product_id=product.product_id, **img.model_dump()))

        # Додавання атрибутів
        for attr in schema.attributes:
            self.session.add(ProductAttribute(product_id=product.product_id, **attr.model_dump()))

        # Додавання магазинів
        for st_id in schema.store_ids:
            self.session.add(ProductStore(product_id=product.product_id, store_id=st_id))

        await self.session.commit()
        return await self.get_product_by_id(product.product_id)

    async def get_product_by_id(self, product_id: int) -> ProductDetailResponse:
        product = await self._get_product_or_404(product_id)

        categories_resp = []
        for pc in product.categories:
            full_path = await self.category_service.build_full_path(pc.category) if pc.category else None
            categories_resp.append(
                ProductCategoryResponse(
                    product_category_id=pc.product_category_id,
                    product_id=pc.product_id,
                    category_id=pc.category_id,
                    category_name=pc.category.name if pc.category else None,
                    full_path=full_path
                )
            )

        stores_resp = [
            ProductStoreResponse(
                product_store_id=ps.product_store_id,
                product_id=ps.product_id,
                store_id=ps.store_id,
                store_name=ps.store.name if ps.store else None
            )
            for ps in product.stores
        ]

        response = ProductDetailResponse.model_validate(product)
        response.categories = categories_resp
        response.stores = stores_resp
        return response

    async def get_products_list(
            self,
            category_id: Optional[int] = None,
            price_from: Optional[float] = None,
            price_to: Optional[float] = None,
            sort_by: Literal["name", "price", "category"] = "name",
            sort_order: Literal["asc", "desc"] = "asc",
            page: int = 1,
            page_size: int = 20
    ) -> Tuple[List[ProductListItemResponse], int]:
        query = select(Product).options(
            selectinload(Product.categories).selectinload(ProductCategory.category)
        )

        if category_id is not None:
            query = query.join(Product.categories).where(ProductCategory.category_id == category_id)
        if price_from is not None:
            query = query.where(Product.price >= price_from)
        if price_to is not None:
            query = query.where(Product.price <= price_to)

        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.session.execute(count_query)).scalar_one()

        result = await self.session.execute(query)
        products = result.scalars().all()

        # Формування списку з головною категорією та full_path
        items: List[ProductListItemResponse] = []
        for p in products:
            main_cat_name = None
            main_cat_path = None
            if p.categories and p.categories[0].category:
                main_cat = p.categories[0].category
                main_cat_name = main_cat.name
                main_cat_path = await self.category_service.build_full_path(main_cat)

            items.append(ProductListItemResponse(
                product_id=p.product_id,
                name=p.name,
                category_name=main_cat_name,
                full_path=main_cat_path,
                price=p.price
            ))

        # Сортування
        reverse = sort_order == "desc"
        if sort_by == "name":
            items.sort(key=lambda x: x.name, reverse=reverse)
        elif sort_by == "price":
            items.sort(key=lambda x: x.price, reverse=reverse)
        elif sort_by == "category":
            items.sort(key=lambda x: (x.full_path or "", x.name), reverse=reverse)

        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end], total_count

    async def update_product(self, product_id: int, schema: ProductUpdate) -> ProductDetailResponse:
        product = await self._get_product_or_404(product_id)
        update_data = schema.model_dump(exclude_unset=True, exclude={"category_ids"})

        if "seo_keyword" in update_data and update_data["seo_keyword"] != product.seo_keyword:
            existing = await self.session.execute(
                select(Product).where(Product.seo_keyword == update_data["seo_keyword"])
            )
            if existing.scalar_one_or_none():
                raise ProductSeoKeywordAlreadyExistsException(update_data["seo_keyword"])

        for key, value in update_data.items():
            setattr(product, key, value)

        if schema.category_ids is not None:
            await self.session.execute(
                delete(ProductCategory).where(ProductCategory.product_id == product_id)
            )
            for cat_id in schema.category_ids:
                self.session.add(ProductCategory(product_id=product_id, category_id=cat_id))

        await self.session.commit()
        return await self.get_product_by_id(product_id)

    async def delete_product(self, product_id: int) -> None:
        product = await self._get_product_or_404(product_id)
        await self.session.delete(product)
        await self.session.commit()

    # --- Саб-ресурси (Зображення) ---
    async def get_images(self, product_id: int) -> List[ProductImage]:
        await self._get_product_or_404(product_id)
        res = await self.session.execute(select(ProductImage).where(ProductImage.product_id == product_id))
        return list(res.scalars().all())

    async def add_image(self, product_id: int, schema: ProductImageBase) -> ProductImage:
        await self._get_product_or_404(product_id)
        image = ProductImage(product_id=product_id, **schema.model_dump())
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def update_image_sort(self, product_id: int, image_id: int, sort_order: int) -> ProductImage:
        res = await self.session.execute(
            select(ProductImage).where(ProductImage.product_id == product_id, ProductImage.product_image_id == image_id)
        )
        img = res.scalar_one_or_none()
        if not img:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        img.sort_order = sort_order
        await self.session.commit()
        await self.session.refresh(img)
        return img

    async def delete_image(self, product_id: int, image_id: int) -> None:
        res = await self.session.execute(
            select(ProductImage).where(ProductImage.product_id == product_id, ProductImage.product_image_id == image_id)
        )
        img = res.scalar_one_or_none()
        if not img:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        await self.session.delete(img)
        await self.session.commit()

    # --- Саб-ресурси (Категорії) ---
    async def add_category(self, product_id: int, category_id: int) -> ProductCategory:
        await self._get_product_or_404(product_id)
        pc = ProductCategory(product_id=product_id, category_id=category_id)
        self.session.add(pc)
        await self.session.commit()
        await self.session.refresh(pc)
        return pc

    async def delete_category(self, product_id: int, product_category_id: int) -> None:
        res = await self.session.execute(
            select(ProductCategory).where(ProductCategory.product_id == product_id,
                                          ProductCategory.product_category_id == product_category_id)
        )
        pc = res.scalar_one_or_none()
        if not pc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product category relation not found")
        await self.session.delete(pc)
        await self.session.commit()

    # --- Саб-ресурси (Атрибути) ---
    async def get_attributes(self, product_id: int) -> List[ProductAttribute]:
        await self._get_product_or_404(product_id)
        res = await self.session.execute(select(ProductAttribute).where(ProductAttribute.product_id == product_id))
        return list(res.scalars().all())

    async def add_attribute(self, product_id: int, schema: ProductAttributeBase) -> ProductAttribute:
        await self._get_product_or_404(product_id)
        attr = ProductAttribute(product_id=product_id, **schema.model_dump())
        self.session.add(attr)
        await self.session.commit()
        await self.session.refresh(attr)
        return attr

    async def update_attribute(self, product_id: int, attribute_id: int,
                               schema: ProductAttributeBase) -> ProductAttribute:
        res = await self.session.execute(
            select(ProductAttribute).where(ProductAttribute.product_id == product_id,
                                           ProductAttribute.product_attribute_id == attribute_id)
        )
        attr = res.scalar_one_or_none()
        if not attr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        for k, v in schema.model_dump().items():
            setattr(attr, k, v)
        await self.session.commit()
        await self.session.refresh(attr)
        return attr

    async def delete_attribute(self, product_id: int, attribute_id: int) -> None:
        res = await self.session.execute(
            select(ProductAttribute).where(ProductAttribute.product_id == product_id,
                                           ProductAttribute.product_attribute_id == attribute_id)
        )
        attr = res.scalar_one_or_none()
        if not attr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        await self.session.delete(attr)
        await self.session.commit()

    # --- 7. Отримання окремого зображення по ID ---
    async def get_image_by_id(self, product_id: int, image_id: int) -> ProductImage:
        res = await self.session.execute(
            select(ProductImage).where(
                ProductImage.product_id == product_id,
                ProductImage.product_image_id == image_id
            )
        )
        img = res.scalar_one_or_none()
        if not img:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        return img

    # --- 12. Отримання окремої категорії товару по ID ---
    async def get_product_category_by_id(self, product_id: int,
                                         product_category_id: int) -> ProductCategoryResponse:
        res = await self.session.execute(
            select(ProductCategory)
            .options(selectinload(ProductCategory.category))
            .where(
                ProductCategory.product_id == product_id,
                ProductCategory.product_category_id == product_category_id
            )
        )
        pc = res.scalar_one_or_none()
        if not pc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product category relation not found")

        full_path = await self.category_service.build_full_path(pc.category) if pc.category else None
        return ProductCategoryResponse(
            product_category_id=pc.product_category_id,
            product_id=pc.product_id,
            category_id=pc.category_id,
            category_name=pc.category.name if pc.category else None,
            full_path=full_path
        )

    # --- 16. Отримання окремого атрибута по ID ---
    async def get_attribute_by_id(self, product_id: int, attribute_id: int) -> ProductAttribute:
        res = await self.session.execute(
            select(ProductAttribute).where(
                ProductAttribute.product_id == product_id,
                ProductAttribute.product_attribute_id == attribute_id
            )
        )
        attr = res.scalar_one_or_none()
        if not attr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        return attr

    # --- 21. Отримання окремого магазину товару по ID ---
    async def get_store_by_id(self, product_id: int, product_store_id: int) -> ProductStoreResponse:
        res = await self.session.execute(
            select(ProductStore)
            .options(selectinload(ProductStore.store))
            .where(
                ProductStore.product_id == product_id,
                ProductStore.product_store_id == product_store_id
            )
        )
        ps = res.scalar_one_or_none()
        if not ps:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product store relation not found")

        return ProductStoreResponse(
            product_store_id=ps.product_store_id,
            product_id=ps.product_id,
            store_id=ps.store_id,
            store_name=ps.store.name if ps.store else None
        )

