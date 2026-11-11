# Кастомні винятки (ProductNotFound)
from fastapi import HTTPException, status


class ProductNotFoundException(HTTPException):
    def __init__(self, product_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"product with id {product_id} not found"
        )

class ProductSeoKeywordAlreadyExistsException(HTTPException):
    def __init__(self, seo_keyword: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SEO keyword '{seo_keyword}' already exists"
        )
