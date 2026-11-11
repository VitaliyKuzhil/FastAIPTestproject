# FastAIPTestproject

Модульний, domain-driven REST API для e-commerce платформи, побудований з використанням **FastAPI**, **SQLAlchemy 2.0 (async)**, **Alembic** та **MySQL**. Проєкт повністю контейнеризований за допомогою **Docker** та включає реверс-проксі на базі **Apache2**.

---

## Технологічний стек

* **Python 3.12** / **FastAPI**
* **SQLAlchemy 2.0** (асинхронний режим) + **Greenlet**
* **Alembic** (управління міграціями БД)
* **MySQL 8.0**
* **Apache2** (реверс-проксі, `mod_proxy`)
* **Docker** & **Docker Compose**
* **phpMyAdmin** (веб-інтерфейс для керування БД)

---

## Кроки для локального розгортання

### 1. Клонування репозиторію

Отримайте код проєкту з GitHub та перейдіть у директорію проєкту:

```bash
git clone https://github.com/VitaliyKuzhil/FastAIPTestproject.git
cd FastAPITestProject
```

### 2. Налаштування змінних середовища (`.env`)

Створіть файл `.env` у кореневій папці проєкту на основі шаблону `.env.example`:

```bash
cp .env.example .env
```

> **Важливо:** Переконайтеся, що хост бази даних у змінній `DATABASE_URL` вказує на назву сервісу MySQL у Docker — `mysql_db_container` або `db` (наприклад, `mysql+aiomysql://user:password@mysql_db_container:3306/fast_api_db`).

### 3. Запуск Docker-контейнерів

> **⚠️ КРИТИЧНО ВАЖЛИВО:** Контейнер Apache2 у Docker налаштований на прослуховування порту **80**. Якщо на вашому хості (комп'ютері) вже працює локальний веб-сервер (Apache, Nginx, Skype тощо) на 80 порту, Docker-контейнер не зможе запуститися.
> **Обов'язково вимкніть локальний Apache перед запуском:**
>
> * **Linux (Ubuntu/Debian):** `sudo systemctl stop apache2`
> * **macOS:** `sudo apachectl stop`

Зберіть та запустіть усі контейнери у фоновому режимі:

```bash
docker compose up --build -d
```

Перевірте статус запущених контейнерів:

```bash
docker compose ps
```

Після успішного запуску будуть доступні наступні сервіси:

* **Swagger UI через Apache (порт 80):** `http://localhost/docs`
* **Swagger UI напряму (порт 8000):** `http://localhost:8000/docs`
* **phpMyAdmin:** `http://localhost:8080`
* **OpenAPI JSON:** `http://localhost/openapi.json`

---

### 4. Виконання міграцій бази даних (Alembic)

У цьому проєкті обрано **ручний режим контролю міграцій** для запобігання небажаним автоматичним змінам схеми при кожному старті контейнера.

Після першого запуску контейнерів виконайте міграцію для створення всіх необхідних таблиць у MySQL:

```bash
docker compose exec api alembic upgrade head
```

Зайдіть у **phpMyAdmin** (`http://localhost:8080`) та перевірте наявність створених таблиць (`category`, `product`, `manufacturer`, `store` тощо).

---

### 5. Заповнення бази даних демо-даними (Seeder)

Для зручного тестування API (зокрема через імпортовану колекцію Postman), заповніть базу даних початковими даними:

```bash
docker compose exec api python src/seed.py
```

*(Примітка: якщо в кінці виконання з'явиться повідомлення `RuntimeError: Event loop is closed`, це безпечний побічний ефект закриття з'єднань бібліотекою `aiomysql`. Демо-дані успішно зберігаються в базу).*

---

## Тестування API (Postman)

У корінній папці проєкту знаходиться готовий файл колекції Postman:  
**`FastAPITestProject.postman_collection.json`**

### Як імпортувати та протестувати:
1. Відкрийте програму **Postman**.
2. Натисніть кнопку **Import** у верхньому лівому кутку.
3. Перетягніть або виберіть файл `FastAPITestProject.postman_collection.json` з кореня проєкту.
4. Після імпорту ви отримаєте повністю згенеровану структуровану колекцію запитів до всіх **26 ендпоінтів** (Категорії, Продукти, Атрибути, Магазини, Зображення).

---

## Зупинка сервісів

Щоб просто **зупинити** контейнери (без видалення мереж та томів збереження даних):

```bash
docker compose stop
```

Щоб повністю **зупинити та видалити** контейнери і мережі:

```bash
docker compose down
```

*(Додайте прапорець `-v` до командування, якщо бажаєте видалити збережені дані бази MySQL: `docker compose down -v`)*

---

## Робота з міграціями під час розробки

Якщо ви додаєте нові моделі або змінюєте існуючі в доменах:

### 1. Реєстрація моделі
Переконайтеся, що нову модель імпортовано у файлі `src/models.py`:
```python
from src.category.models import Category
from src.product.models import Product
from src.manufacturer.models import Manufacturer
from src.store.models import Store
from src.your_new_domain.models import YourModel  # Додати імпорт
```

### 2. Генерація нової міграції
```bash
docker compose exec api alembic revision --autogenerate -m "Опис змін"
```

### 3. Застосування міграції
```bash
docker compose exec api alembic upgrade head
```

---

## Структура проекту

```text
FastAPITestProject/
├── alembic/                                # Конфігурація та скрипти міграцій Alembic
├── apache/                                 # Конфігурація веб-сервера Apache2 (Reverse Proxy)
│   └── httpd.conf
├── src/                                    # Основний вихідний код API
│   ├── category/                           # Домен категорій (models, schemas, service, router)
│   ├── manufacturer/                       # Домен виробників (models, schemas, service, router)
│   ├── product/                            # Домен продуктів (models, schemas, service, router)
│   ├── store/                              # Домен магазинів (models, schemas, service, router)
│   ├── __init__.py
│   ├── config.py                           # Налаштування Pydantic Settings
│   ├── database.py                         # Async SQLAlchemy Engine & SessionMaker
│   ├── main.py                             # Точка входу FastAPI
│   ├── models.py                           # Загальний Base metadata та реєстрація моделей
│   └── seed.py                             # Скрипт для заповнення БД демо-даними
├── .dockerignore                           # Виключення для Docker
├── .env                                    # Змінні середовища (не зберігається в Git)
├── .env.example                            # Шаблон змінних середовища
├── .gitignore                              # Виключення для Git
├── alembic.ini                             # Конфігураційний файл Alembic
├── docker-compose.yml                      # Опис 4 Docker-сервісів (api, mysql, phpmyadmin, apache)
├── Dockerfile                              # Конструктор образу FastAPI
├── FastAPITestProject.postman_collection.json  # Збережена колекція Postman для тестування
├── LICENSE                                 # Ліцензія
├── README.md                               # Документація проєкту
└── requirements.txt                        # Залежності Python
```