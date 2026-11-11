from fastapi import FastAPI
from src.config import settings
from src.category.router import router as category_router

app = FastAPI(title=settings.APP_TITLE)

app.include_router(category_router)

@app.get("/")
async def root():
    return {"message": "Infrastructure is up and running!"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
