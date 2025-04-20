# ISP Compare

<p align="center">
  <img src="https://img.shields.io/badge/status-diploma%20project-blue" alt="Project Status"/>
  <img src="https://img.shields.io/badge/python-3.13-blue" alt="Python Version"/>
  <img src="https://img.shields.io/badge/fastapi-0.115-blue" alt="FastAPI Version"/>
</p>
Веб-сервис для сравнения интернет-провайдеров по качеству и стоимости услуг

## 📝 Описание

ISP Compare - это веб-сервис, предназначенный для пользователей, которым необходим удобный инструмент для эффективного
сравнения и выбора интернет-провайдеров. С его помощью можно анализировать качество предоставляемых услуг, сравнивать
стоимость тарифных планов различных провайдеров и получать актуальную информацию о доступности услуг.

## 🛠️ Технический стек

### Backend

- Python 3.13
- FastAPI - асинхронный веб-фреймворк
- SQLAlchemy - ORM для работы с базой данных
- Dishka - DI фреймворк
- JWT - для авторизации пользователей
- Alembic - для миграций базы данных

### Frontend

- JavaScript
- React

### Инфраструктура

- PostgreSQL - реляционная база данных
- Redis - для хранения черного списка токенов и кеширования
- Docker - контейнеризация
- Docker Compose - оркестрация контейнеров

## 🗂️ Структура проекта

```
.
├── backend/                        # Серверная часть приложения
│   ├── src/                        # Исходный код
│   │   └── isp_compare/            # Основной модуль приложения
│   │       ├── api/                # API endpoints
│   │       │   └── v1/             # Версия API
│   │       ├── core/               # Конфигурация и ядро приложения
│   │       │   └── di/             # Настройки DI
│   │       ├── models/             # Модели базы данных
│   │       ├── repositories/       # Репозитории для доступа к данным
│   │       ├── schemas/            # Pydantic схемы для валидации данных
│   │       ├── services/           # Бизнес-логика
│   │       └── main.py             # Точка входа в приложение
│   ├── migrations/                 # Миграции базы данных (Alembic)
│   │   └── versions/               # Версии миграций
│   ├── scripts/                    # Скрипты для развертывания
│   ├── tests/                      # Тесты
│   ├── Dockerfile                  # Docker-конфигурация для backend
│   ├── pyproject.toml              # Зависимости и метаданные проекта
│   └── poetry.lock                 # Зафиксированные версии зависимостей
├── frontend/                       # Клиентская часть приложения
│   ├── src/                        # Исходный код
│   └── package.json                # Зависимости и скрипты
├── docker-compose.yml              # Конфигурация Docker Compose
├── .env.example                    # Пример файла с переменными окружения
└── README.md                       # Этот файл
```

## 🚀 Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Git

### Шаги установки

1. Клонируйте репозиторий:

```bash
git clone https://github.com/bodaue/isp-compare.git
cd isp-compare
```

2. Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

3. Отредактируйте файл `.env`, настроив необходимые переменные окружения

4. Запустите приложение с помощью Docker Compose:

```bash
docker-compose up --build
```

5. Приложение будет доступно по адресу:
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000
    - API документация: http://localhost:8000/docs

## 📚 API Документация

После запуска приложения API документация доступна по адресу: http://localhost:8000/docs (Swagger UI)
или http://localhost:8000/redoc (ReDoc).

## 🔒 Аутентификация

Сервис использует JWT для аутентификации. Токены доступа выдаются после авторизации пользователя и должны быть включены
в заголовок `Authorization` для защищенных эндпоинтов.

```
Authorization: Bearer <access_token>
```