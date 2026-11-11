from fastapi import FastAPI
from src.config import settings
from src.category.router import router as category_router
from src.product.router import router as product_router
from src.manufacturer.models import Manufacturer
from src.product.models import Product
from src.category.models import Category
from src.store.models import Store

app = FastAPI(title=settings.APP_TITLE)

app.include_router(category_router)
app.include_router(product_router)

@app.get("/")
async def root():
    return {"message": "Infrastructure is up and running!"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
