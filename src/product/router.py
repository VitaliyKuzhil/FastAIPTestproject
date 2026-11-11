# Ендпоінти (GET, POST, PATCH, DELETE)
from typing import Optional, Literal, List
from fastapi import APIRouter, Depends, Query, status

from src.product.schemas import (
    ProductCreate, ProductUpdate, ProductDetailResponse, ProductListResponse,
    ProductImageResponse, ProductImageBase,
    ProductCategoryResponse,
    ProductAttributeResponse, ProductAttributeBase,
    ProductStoreResponse
)
from src.product.service import ProductService

router = APIRouter(
    prefix="/product",
    tags=["Product"]
)

# 1. GET /product
@router.get("", response_model=ProductListResponse)
async def get_products(
    category_id: Optional[int] = Query(None, description="Фільтр за категорією"),
    price_from: Optional[float] = Query(None, ge=0, description="Ціна від"),
    price_to: Optional[float] = Query(None, ge=0, description="Ціна до"),
    sort_by: Literal["name", "price", "category"] = Query("name", description="Сортувати за полем"),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Напрямок сортування"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ProductService = Depends(ProductService)
):
    items, total = await service.get_products_list(
        category_id=category_id,
        price_from=price_from,
        price_to=price_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    return ProductListResponse(items=items, total=total)

# 2. GET /product/{product_id}
@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(product_id: int, service: ProductService = Depends(ProductService)):
    return await service.get_product_by_id(product_id)

# 3. POST /product
@router.post("", response_model=ProductDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_product(schema: ProductCreate, service: ProductService = Depends(ProductService)):
    return await service.create_product(schema)

# 4. PATCH /product/{product_id}
@router.patch("/{product_id}", response_model=ProductDetailResponse)
async def update_product(product_id: int, schema: ProductUpdate, service: ProductService = Depends(ProductService)):
    return await service.update_product(product_id, schema)

# 5. DELETE /product/{product_id}
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, service: ProductService = Depends(ProductService)):
    await service.delete_product(product_id)

# --- Зображення ---
# 6. GET /product/{product_id}/image
@router.get("/{product_id}/image", response_model=List[ProductImageResponse])
async def get_images(product_id: int, service: ProductService = Depends(ProductService)):
    return await service.get_images(product_id)

# 8. POST /product/{product_id}/image
@router.post("/{product_id}/image", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
async def add_image(product_id: int, schema: ProductImageBase, service: ProductService = Depends(ProductService)):
    return await service.add_image(product_id, schema)

# 9. PATCH /product/{product_id}/image/{product_image_id}
@router.patch("/{product_id}/image/{product_image_id}", response_model=ProductImageResponse)
async def update_image(product_id: int, product_image_id: int, sort_order: int = Query(...), service: ProductService = Depends(ProductService)):
    return await service.update_image_sort(product_id, product_image_id, sort_order)

# 10. DELETE /product/{product_id}/image/{product_image_id}
@router.delete("/{product_id}/image/{product_image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(product_id: int, product_image_id: int, service: ProductService = Depends(ProductService)):
    await service.delete_image(product_id, product_image_id)

# --- Категорії товару ---
# 11. GET /product/{product_id}/category
@router.get("/{product_id}/category", response_model=List[ProductCategoryResponse])
async def get_product_categories(product_id: int, service: ProductService = Depends(ProductService)):
    product = await service.get_product_by_id(product_id)
    return product.categories

# 13. POST /product/{product_id}/category
@router.post("/{product_id}/category", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def add_product_category(product_id: int, category_id: int = Query(...), service: ProductService = Depends(ProductService)):
    pc = await service.add_category(product_id, category_id)
    return ProductCategoryResponse.model_validate(pc)

# 14. DELETE /product/{product_id}/category/{product_category_id}
@router.delete("/{product_id}/category/{product_category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_category(product_id: int, product_category_id: int, service: ProductService = Depends(ProductService)):
    await service.delete_category(product_id, product_category_id)

# --- Атрибути товару ---
# 15. GET /product/{product_id}/attribute
@router.get("/{product_id}/attribute", response_model=List[ProductAttributeResponse])
async def get_attributes(product_id: int, service: ProductService = Depends(ProductService)):
    return await service.get_attributes(product_id)

# 17. POST /product/{product_id}/attribute
@router.post("/{product_id}/attribute", response_model=ProductAttributeResponse, status_code=status.HTTP_201_CREATED)
async def add_attribute(product_id: int, schema: ProductAttributeBase, service: ProductService = Depends(ProductService)):
    return await service.add_attribute(product_id, schema)

# 18. PATCH /product/{product_id}/attribute/{product_attribute_id}
@router.patch("/{product_id}/attribute/{product_attribute_id}", response_model=ProductAttributeResponse)
async def update_attribute(product_id: int, product_attribute_id: int, schema: ProductAttributeBase, service: ProductService = Depends(ProductService)):
    return await service.update_attribute(product_id, product_attribute_id, schema)

# 19. DELETE /product/{product_id}/attribute/{product_attribute_id}
@router.delete("/{product_id}/attribute/{product_attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attribute(product_id: int, product_attribute_id: int, service: ProductService = Depends(ProductService)):
    await service.delete_attribute(product_id, product_attribute_id)

# --- Магазини товару ---
# 20. GET /product/{product_id}/store
@router.get("/{product_id}/store", response_model=List[ProductStoreResponse])
async def get_product_stores(product_id: int, service: ProductService = Depends(ProductService)):
    product = await service.get_product_by_id(product_id)
    return product.stores

# 7. GET /product/{product_id}/image/{product_image_id}
@router.get("/{product_id}/image/{product_image_id}", response_model=ProductImageResponse)
async def get_image(product_id: int, product_image_id: int, service: ProductService = Depends(ProductService)):
    """Отримати конкретне додаткове зображення товару."""
    return await service.get_image_by_id(product_id, product_image_id)


# 12. GET /product/{product_id}/category/{product_category_id}
@router.get("/{product_id}/category/{product_category_id}", response_model=ProductCategoryResponse)
async def get_product_category(product_id: int, product_category_id: int, service: ProductService = Depends(ProductService)):
    """Отримати конкретну прив'язану категорію товару (з назвою та повним шляхом)."""
    return await service.get_product_category_by_id(product_id, product_category_id)


# 16. GET /product/{product_id}/attribute/{product_attribute_id}
@router.get("/{product_id}/attribute/{product_attribute_id}", response_model=ProductAttributeResponse)
async def get_attribute(product_id: int, product_attribute_id: int, service: ProductService = Depends(ProductService)):
    """Отримати конкретну характеристику (атрибут) товару."""
    return await service.get_attribute_by_id(product_id, product_attribute_id)


# 21. GET /product/{product_id}/store/{product_store_id}
@router.get("/{product_id}/store/{product_store_id}", response_model=ProductStoreResponse)
async def get_product_store(product_id: int, product_store_id: int, service: ProductService = Depends(ProductService)):
    """Отримати конкретний прив'язаний магазин товару."""
    return await service.get_store_by_id(product_id, product_store_id)
