# Кастомні винятки (CategoryNotFound)
from fastapi import HTTPException, status


class CategoryNotFoundException(HTTPException):
    def __init__(self, category_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )


class InvalidParentCategoryException(HTTPException):
    def __init__(self, detail: str = "Category cannot be its own parent"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
