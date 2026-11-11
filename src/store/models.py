from sqlalchemy import Column, Integer, String
from src.models import Base
from src.store.constants import (
    MAX_STORE_NAME_LENGTH,
    MAX_URL_LENGTH,
)

class Store(Base):
    __tablename__ = "store"

    store_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(MAX_STORE_NAME_LENGTH), nullable=False, index=True)
    url = Column(String(MAX_URL_LENGTH), nullable=True)