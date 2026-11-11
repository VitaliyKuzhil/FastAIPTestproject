# SQLAlchemy модель (таблиця category)
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from src.models import Base
from src.category.constants import (
    CategoryStatus,
    MAX_CATEGORY_NAME_LENGTH,
    MAX_SEO_KEYWORD_LENGTH,
    MAX_META_TITLE_LENGTH,
    MAX_META_KEYWORD_LENGTH,
    MAX_IMAGE_PATH_LENGTH,
)


class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(MAX_CATEGORY_NAME_LENGTH), nullable=False)
    description = Column(Text, nullable=True)

    # Relationship for categories (NULL = main category)
    parent_category_id = Column(
        Integer,
        ForeignKey("category.category_id", ondelete="CASCADE"),
        nullable=True
    )

    # SEO field
    seo_keyword = Column(String(MAX_SEO_KEYWORD_LENGTH), nullable=True)
    meta_title = Column(String(MAX_META_TITLE_LENGTH), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keyword = Column(String(MAX_META_KEYWORD_LENGTH), nullable=True)

    image = Column(String(MAX_IMAGE_PATH_LENGTH), nullable=True)
    status = Column(Enum(CategoryStatus), default=CategoryStatus.ACTIVE, nullable=False)

    # Auto date
    date_added = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modify = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Recursive connection with remote side
    subcategories = relationship(
        "Category",
        backref=backref("parent", remote_side=[category_id]),
        cascade="all, delete-orphan"
    )
