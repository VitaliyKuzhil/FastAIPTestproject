# Pydantic моделі (валідація)
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from src.category.constants import (
    CategoryStatus,
    MAX_CATEGORY_NAME_LENGTH,
    MAX_SEO_KEYWORD_LENGTH,
    MAX_META_TITLE_LENGTH,
    MAX_META_KEYWORD_LENGTH,
    MAX_IMAGE_PATH_LENGTH,
)

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=MAX_CATEGORY_NAME_LENGTH)
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    seo_keyword: Optional[str] = Field(None, max_length=MAX_SEO_KEYWORD_LENGTH)
    meta_title: Optional[str] = Field(None, max_length=MAX_META_TITLE_LENGTH)
    meta_description: Optional[str] = None
    meta_keyword: Optional[str] = Field(None, max_length=MAX_META_KEYWORD_LENGTH)
    image: Optional[str] = Field(None, max_length=MAX_IMAGE_PATH_LENGTH)
    status: CategoryStatus = CategoryStatus.ACTIVE

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=MAX_CATEGORY_NAME_LENGTH)
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    seo_keyword: Optional[str] = Field(None, max_length=MAX_SEO_KEYWORD_LENGTH)
    meta_title: Optional[str] = Field(None, max_length=MAX_META_TITLE_LENGTH)
    meta_description: Optional[str] = None
    meta_keyword: Optional[str] = Field(None, max_length=MAX_META_KEYWORD_LENGTH)
    image: Optional[str] = Field(None, max_length=MAX_IMAGE_PATH_LENGTH)
    status: Optional[CategoryStatus] = None

class CategoryResponse(CategoryBase):
    category_id: int
    date_added: datetime
    date_modify: datetime
    full_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
