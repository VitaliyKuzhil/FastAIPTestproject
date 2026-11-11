# SQLAlchemy модель (таблиця product)
from sqlalchemy import Column, Integer, String, Text, Numeric, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models import Base
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


class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(MAX_PRODUCT_NAME_LENGTH), nullable=False, index=True)
    description = Column(Text, nullable=True)
    seo_keyword = Column(String(MAX_SEO_KEYWORD_LENGTH), nullable=True, unique=True, index=True)
    meta_title = Column(String(MAX_META_TITLE_LENGTH), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keyword = Column(String(MAX_META_KEYWORD_LENGTH), nullable=True)
    image = Column(String(MAX_IMAGE_PATH_LENGTH), nullable=True)
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE)

    date_added = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modify = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    price = Column(Numeric(10, 2), nullable=False)
    model = Column(String(MAX_MODEL_LENGTH), nullable=True)
    manufacturer_id = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True, default=0.0)
    viewed = Column(Integer, nullable=False, default=0)

    # Relationships
    categories = relationship("ProductCategory", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")


class ProductCategory(Base):
    __tablename__ = "product_category"

    product_category_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.category_id", ondelete="CASCADE"), nullable=False)

    product = relationship("Product", back_populates="categories")


class ProductImage(Base):
    __tablename__ = "product_image"

    product_image_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id", ondelete="CASCADE"), nullable=False)
    image = Column(String(MAX_IMAGE_PATH_LENGTH), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="images")


class ProductAttribute(Base):
    __tablename__ = "product_attribute"

    product_attribute_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id", ondelete="CASCADE"), nullable=False)
    group_name = Column(String(MAX_ATTRIBUTE_GROUP_NAME_LENGTH), nullable=False)
    name = Column(String(MAX_ATTRIBUTE_NAME_LENGTH), nullable=False)
    value = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="attributes")
