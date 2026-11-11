# Pydantic моделі (валідація)
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from src.product.constants import (
    ProductStatus,
    MAX_PRODUCT_NAME_LENGTH,
    MAX_SEO_KEYWORD_LENGTH,
    MAX_META_TITLE_LENGTH,
    MAX_META_KEYWORD_LENGTH,
    MAX_IMAGE_PATH_LENGTH,
    MAX_MODEL_LENGTH,
    MAX_ATTRIBUTE_GROUP_NAME_LENGTH,
    MAX_ATTRIBUTE_NAME_LENGTH
)


class ProductImageBase(BaseModel):
    image: str = Field(..., max_length=MAX_IMAGE_PATH_LENGTH)
    sort_order: int = 0


class ProductImageResponse(ProductImageBase):
    product_image_id: int
    product_id: int
    model_config = ConfigDict(from_attributes=True)


class ProductAttributeBase(BaseModel):
    group_name: str = Field(..., max_length=MAX_ATTRIBUTE_GROUP_NAME_LENGTH)
    name: str = Field(..., max_length=MAX_ATTRIBUTE_NAME_LENGTH)
    value: str
    sort_order: int = 0


class ProductAttributeResponse(ProductAttributeBase):
    product_attribute_id: int
    product_id: int
    model_config = ConfigDict(from_attributes=True)

class ProductCategoryResponse(BaseModel):
    product_category_id: int
    product_id: int
    category_id: int
    category_name: Optional[str] = None
    full_path: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ProductStoreResponse(BaseModel):
    product_store_id: int
    product_id: int
    store_id: int
    store_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ManufacturerResponse(BaseModel):
    manufacturer_id: int
    name: str
    image: Optional[str] = None
    sort_order: int = 0
    model_config = ConfigDict(from_attributes=True)


# --- Основні схеми товару ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=MAX_PRODUCT_NAME_LENGTH)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    model: Optional[str] = Field(None, max_length=MAX_MODEL_LENGTH)
    manufacturer_id: Optional[int] = None

    seo_keyword: Optional[str] = Field(None, max_length=MAX_SEO_KEYWORD_LENGTH)
    meta_title: Optional[str] = Field(None, max_length=MAX_META_TITLE_LENGTH)
    meta_description: Optional[str] = None
    meta_keyword: Optional[str] = Field(None, max_length=MAX_META_KEYWORD_LENGTH)

    image: Optional[str] = Field(None, max_length=MAX_IMAGE_PATH_LENGTH)
    status: ProductStatus = ProductStatus.ACTIVE
    rating: float = 0.0
    viewed: int = 0


class ProductCreate(ProductBase):
    category_ids: List[int] = Field(default_factory=list, description="List of Category IDs")
    images: List[ProductImageBase] = Field(default_factory=list)
    attributes: List[ProductAttributeBase] = Field(default_factory=list)
    store_ids: List[int] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=MAX_PRODUCT_NAME_LENGTH)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    model: Optional[str] = Field(None, max_length=MAX_MODEL_LENGTH)
    manufacturer_id: Optional[int] = None

    seo_keyword: Optional[str] = Field(None, max_length=MAX_SEO_KEYWORD_LENGTH)
    meta_title: Optional[str] = Field(None, max_length=MAX_META_TITLE_LENGTH)
    meta_description: Optional[str] = None
    meta_keyword: Optional[str] = Field(None, max_length=MAX_META_KEYWORD_LENGTH)

    image: Optional[str] = Field(None, max_length=MAX_IMAGE_PATH_LENGTH)
    status: Optional[ProductStatus] = None

    category_ids: Optional[List[int]] = None


class ProductListItemResponse(BaseModel):
    product_id: int
    name: str
    category_name: Optional[str] = None
    full_path: Optional[str] = None
    price: Decimal

    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    items: List[ProductListItemResponse]
    total: int


class ProductDetailResponse(ProductBase):
    product_id: int
    date_added: datetime
    date_modify: datetime

    categories: List[ProductCategoryResponse] = []
    images: List[ProductImageBase] = []
    attributes: List[ProductAttributeBase] = []
    stores: List[ProductStoreResponse] = []
    manufacturer: Optional[ManufacturerResponse] = None

    model_config = ConfigDict(from_attributes=True)
