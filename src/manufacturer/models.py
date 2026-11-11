from sqlalchemy import Column, Integer, String
from src.models import Base
from src.manufacturer.constants import (
    MAX_MANUFACTURER_NAME_LENGTH,
    MAX_IMAGE_PATH_LENGTH,
)

class Manufacturer(Base):
    __tablename__ = "manufacturer"

    manufacturer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(MAX_MANUFACTURER_NAME_LENGTH), nullable=False, index=True)
    image = Column(String(MAX_IMAGE_PATH_LENGTH), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)