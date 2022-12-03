# BREAD BOT
## Author: Lev Kudryashov
Данный проект является телеграм-ботом для локальных чатов.
Бот выполнен на стеке:
- python version 3.11.0
- SQLAlchemy для взаимодействия с БД
- Alembic для реализации миграций в БД
- FastAPI как веб-фреймворк
- Pydantic как сериализатор и валидатор данных
- Opensensus как инструмент для телеметрии и трассировки

### О структуре приложения:
- пакет `main` - Центральный директорий приложения, который содержит настройки, конфигурации веб-фраймворка, celery
    - пакет `settings` - Содержит настройки приложения.
      - модуль [__init__.py](bread_bot/main/settings/__init__.py) - Точка входа в настройки
      - модуль [default.py](bread_bot/main/settings/default.py) - Модуль, содержащий основные настройки приложения
    - `database` Пакет содержит инструменты для упрощения и улучшения работы с ORM
       - [mixins.py](bread_bot/main/database/mixins.py) - Основные миксины для расширения моделей для удобства работы с сущностями и моделями БД и бизнес-логики
       - [base.py](bread_bot/main/database/base.py) - Инициализация объектов джижков и сессий до БД
    - модуль [webserver.py](bread_bot/main/webserver.py) - Центральная конфигурация и инициализация FastApi приложения
- пакет [tests](bread_bot/tests) - Тесты приложения
- пакет `alembic` - это центральный пакет для осуществления автогенерации миграций/миграций/отката миграций в БД. [Подробнее можно почитать здесь про данный инструмент](bread_bot/alembic/README.md)
    - пакет `versions` - пакет с миграциями файлов
    - модуль [env.py](bread_bot/alembic/env.py) - Конфигурационный модуль для миграций
- пакет-приложение `my_app` - Это пакет-приложения сущностей. Созданная для примера. Здесь необходимо реализовывать модели, маршруты и бизнес-логику с сущностями бизнес-логики.
    - пакет `models` - пакет с модулями-классами сущностей БД 
    - пакет `routes` - содержит маршруты для api приложения с определенной бизнес-логикой
    - пакет `schemas` - содержит схемы сериализации/десериализации бизнес-сущностей Pydantic
- пакет-приложение `auth` - Пакет приложение сущностей с пользователями, авторизационными методами, способами аутентификации, реализации токенов OAuth2 by JWT
- `utils` - стандартный пакет с прикладными утилитами
  - модуль [base_client.py](bread_bot/utils/base_client.py) является абстрактным классом-родителей для всех http-клиентов (Скоро будет изменен. В процессе реализации по паттерну Фабрика)
  - модуль [custom_json_logger.py](bread_bot/utils/json_logger.py) содержит классы-форматтеры логов для централизации логов в json формат
  - модуль [middlewares.py](bread_bot/utils/middlewares.py) содержит перечень Middleware-обработчиков для запросов по HTTP в сервер. (Логгер запросов, например)
  - модуль [dependencies.py](bread_bot/utils/dependencies.py) содержит классы и функции зависимостей для адресов сервиса (Примеси сессии БД, например)
  - модуль [structs.py](bread_bot/utils/structs.py) здесь будут содержаться константные для проекта(но не для пакета с бизнес-сущностью) структуры для удобства использования
- модуль [server.py](server.py) запускает настроенный веб-сервер приложения
- папка `requirements` - папка с зависимостями проекта
- файл [tox.ini](tox.ini) - Конфигурация для codestyle проекта
# settings Примеры некоторых настроек
Настройка количества воркеров FastAPI, которые будут запущены в одном процессе:
```python
import os

WORKERS_COUNT = int(os.getenv('WORKERS_COUNT', 1))
```
Настройка доступа к БД выглядит следующим образом:

```python
import os

DATABASE_SETTINGS = {
    'default': {
        'database': os.getenv('DB_NAME', 'bread_bot'),
        'user': os.getenv('DB_USER', 'bread_bot'),
        'password': os.getenv('DB_PASSWORD', 'bread_bot'),
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': os.getenv('DB_PORT', '5432'),
    }
}
```
SQLAlchemy сама организует, каким количеством пулов подключений оперировать. Необходимо приложению задавать настройку, какой максимум возможно поддерживать по подключениям:
```python
import os
DB_MAX_POOL = int(os.getenv('DB_MAX_POOL', 20))
```
**Внимание**: Это общее количество воркеров на всё приложение и на все воркеры. То есть, каждому воркеру будет выделена часть сессий, а не все общее количество. 
Иначе говоря в коде ниже каждому из 10ти воркеров будет предъявлено по 5 рабочих сессий БД: 
```python
import math
WORKERS_COUNT = 10
DB_MAX_POOL = 50
DB_POOL_SIZE = max(math.ceil(DB_MAX_POOL / WORKERS_COUNT), 1)
```
Также, если есть необходимость, то можно заниматься ограничением сессий с помощью pgbouncer. Файл настройки pgbouncer: [pgbouncer.ini](pgbouncer/pgbouncer.ini)


Необходимо указывать все используемые приложения в проекте (как в django)
```python
APP_MODULES = [
    'my_app',
    'auth',
]
```

# Web
FastAPI использует в качестве веб-сервера uvicorn. Есть несколько вариантов запуска приложения:
```shell
uvicorn bread_bot.main.webserver:app
```
```shell
python server.py
```

# Документация
Не секрет, что fastapi умеет автодокументировать в swagger, redoc, openapi.json все маршруты и точки входа. Поэтому мой совет как разработчика тщательно описывать схемы Pydantic для удобства и читабельности проекта. Желательно с кейсами использования. Все можно найти в официальной спецификации фреймворка.
# База данных и модели
Реализован CRUDMixin для оперирования простыми командами как get, filter, first, create, update, итд итп. Также асинхронные аналоги данных методов. Расширять данную модель можно до бесконечности

# Зависимости
Самая главная зависимость - это poetry
```shell
pip install poetry
```

Далее оперируется вся работа с зависимостями через него:

### Добавить зависимость
```shell
poetry add requests
```

### Добавить зависимость для разработки

```shell
poetry add pytest --dev
```

### Установить зависимости для разработки
```shell
poetry install
```

### Установить зависимости для прода
```shell
poetry install --only main
```
# QUICK START
Для начала везде, где Вы видите слово `bread_bot` - тут может оказаться наименование вашего микросервиса. Ну логично, да?
Необходимо установить все зависимости в проекте:
```shell
pip install poetry && poetry install
```
Представьте на секунду, что вы уже поставили PostgreSQL. И теперь нужно создать БД с пользователем и паролем:
```postgresql
CREATE DATABASE bread_bot;
CREATE ROLE bread_bot with LOGIN PASSWORD 'my_password';
GRANT ALL PRIVILEGES ON DATABASE bread_bot TO bread_bot;
```
Миграция схемы баз данных
```shell
alembic upgrade head
```
Откат миграции базы данных
```shell
alembic downgrade -1
```
Авто-генерация схемы базы данных
```shell
alembic revision --autogenerate -m 'my migration message'
```
Запускаем локально веб-сервер
```shell
uvicorn bread_bot.main.webserver:app --reload
```
или так:
```shell
python server.py
```
Запустить проверку codestyle проекта (А эта проверка будет работать и при CI)
```shell
flake8
```
Запустить тесты:
```shell
pytest bread_bot/tests
```
Запустить создания данных по покрытию тестами
```shell
coverage run -m pytest bread_bot/tests
```
Запустить вывод отчета по покрытию тестами
```shell
coverage report -m 
```
Запустить вывод отчета в html формате
```shell
coverage html 
```
Удалить данные отчета
```shell
coverage erase
```
Можно использовать последовательность:
```shell
coverage erase && coverage run pytest bread_bot/tests && coverage html
```
Функциональность бота описана в [About.md](About.md)
