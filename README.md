# FastAIPTestproject

Модульний, domain-driven REST API для e-commerce платформи, побудований з використанням **FastAPI**, **SQLAlchemy 2.0 (async)**, **Alembic** та **MySQL**. Проєкт повністю контейнеризований за допомогою **Docker**.

---

## Технологічний стек

- **Python 3.12** / **FastAPI**
- **SQLAlchemy 2.0** (асинхронний режим) + **Greenlet**
- **Alembic** (управління міграціями БД)
- **MySQL 8.0**
- **Docker** & **Docker Compose**
- **phpMyAdmin** (веб-інтерфейс для керування БД)

---

## Кроки для локального розгортання

### 1. Клонування репозиторію

Отримайте код проєкту з GitHub та перейдіть у директорію проєкту:

```bash
git clone https://github.com/VitaliyKuzhil/FastAIPTestproject.git
cd FastAPIProject
```

### 2. Налаштування змінних середовища (`.env`)

Створіть файл `.env` у кореневій папці проєкту на основі шаблону `.env.example`:

```bash
cp .env.example .env
```

> **Важливо:** Переконайтеся, що хост бази даних у змінній `DATABASE_URL` вказує на назву сервісу MySQL у Docker — `mysql_db_container` або `mysql` (наприклад, `mysql+aiomysql://user:password@mysql_db_container:3306/fast_api_db`).

---

### 3. Запуск Docker-контейнерів

Зберіть та запустіть усі контейнери у фоновому режимі:

```bash
docker compose up --build -d
```

Перевірте статус запущених контейнерів:

```bash
docker compose ps
```

Після успішного запуску будуть доступні наступні сервіси:
- **FastAPI application:** `http://localhost:8000`
- **Swagger UI (Interactive API Docs):** `http://localhost:8000/docs`
- **phpMyAdmin:** `http://localhost:8080`

---

### 4. Виконання міграцій бази даних (Alembic)

У цьому проєкті обрано **ручний режим контролю міграцій** для запобігання небажаним автоматичним змінам схеми при кожному старті контейнера.

#### Застосування існуючих міграцій (для Category та Product):

Після першого запуску контейнерів виконайте міграцію для створення таблиць `category` та `product` у MySQL:

```bash
docker compose exec api alembic upgrade head
```

Зайдіть у **phpMyAdmin** (`http://localhost:8080`) та перевірте наявність створених таблиць:
- `alembic_version`
- `category`
- `product`

---

## Робота з міграціями під час розробки

Якщо ви додаєте нові моделі або змінюєте існуючі в доменах (`src/category/models.py`, `src/product/models.py` тощо):

### 1. Реєстрація моделі
Переконайтеся, що нову модель імпортовано у файлі `src/models.py`:
```python
from src.category.models import Category
from src.product.models import Product
from src.your_new_domain.models import YourModel  # Додати імпорт
```

### 2. Генерація нової міграції
Згенеруйте ревізію Alembic на основі порівняння метаданих ORM з поточною БД:
```bash
docker compose exec api alembic revision --autogenerate -m "Опис змін"
```

### 3. Застосування міграції
Застосуйте нову міграцію до бази даних:
```bash
docker compose exec api alembic upgrade head
```

---

## Структура проекту

```text
FastAPITestProject/
├── alembic/              # Конфігурація та скрипти міграцій Alembic
├── alembic.ini           # Конфігураційний файл Alembic
├── docker-compose.yml    # Опис Docker-сервісів (api, mysql, phpmyadmin, apache)
├── Dockerfile            # Конструктор образу FastAPI
├── requirements.txt      # Залежності Python
├── src/
│   ├── config.py         # Налаштування pydantic-settings
│   ├── database.py       # Async SQLAlchemy Engine & SessionMaker
│   ├── main.py           # Точка входу FastAPI
│   ├── models.py         # Загальний Base metadata та реєстрація моделей
│   ├── category/         # Домен категорій (models, schemas, exceptions, constants)
│   └── product/          # Домен продуктів (models, schemas, exceptions, constants)
└── README.md             # Документація проєкту
```