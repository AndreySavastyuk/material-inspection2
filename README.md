# Metal Inspection System

Система приемки и входного контроля металла для металлообрабатывающего предприятия.

## 🎯 Описание

Система предназначена для автоматизации процессов приемки, контроля качества и управления потоком металлических материалов на предприятии. 

### Основные возможности:
- 📦 Приемка и регистрация материалов
- 🔍 Многоуровневый контроль качества
- 🧪 Управление разрушающими и неразрушающими испытаниями
- 📄 Генерация и хранение сертификатов
- 🔄 Автоматизация workflow материалов
- 👥 Ролевая система доступа

## 🛠️ Технологический стек

### Backend:
- **Python 3.13+**
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy 2.0** - ORM с асинхронной поддержкой
- **PostgreSQL** - основная БД (SQLite для разработки)
- **Redis** - кеширование и сессии
- **Alembic** - миграции БД
- **Pydantic** - валидация данных
- **AsyncPG** - асинхронный драйвер PostgreSQL

### Frontend:
- **Vue.js 3.4+** - прогрессивный JS фреймворк
- **Vite** - быстрый сборщик
- **Vue Router** - маршрутизация
- **Pinia** - управление состоянием
- **Axios** - HTTP клиент

## 📋 Требования

- **Python 3.13+**
- **Node.js 18+**
- **PostgreSQL 16+** (опционально, можно использовать SQLite)
- **Redis 7+** (опционально)
- **Docker и Docker Compose** (рекомендуется)

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/AndreySavastyuk/material-inspection2.git
cd material-inspection2
```

### 2. Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv .venv

# Активация окружения
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Копирование файла конфигурации
cp .env.example .env

# Инициализация базы данных
python scripts/init_db.py --sync

# Запуск сервера разработки
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Настройка Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Копирование файла конфигурации
cp .env.example .env

# Запуск dev сервера
npm run dev
```

### 4. Доступ к системе
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost:8000/docs
- **Интерактивная документация**: http://localhost:8000/redoc

## 🐳 Запуск через Docker

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down
```

## 💻 Разработка

### Структура проекта

```
material-inspection2/
├── backend/                 # Python FastAPI backend
│   ├── src/                 # Исходный код
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Основная логика
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── schemas/         # Pydantic схемы
│   │   └── services/        # Бизнес-логика
│   ├── alembic/             # Миграции БД
│   ├── scripts/             # Утилиты
│   └── tests/               # Тесты
├── frontend/                # Vue.js frontend
│   ├── src/                 # Исходный код
│   │   ├── components/      # Vue компоненты
│   │   ├── views/           # Страницы
│   │   ├── stores/          # Pinia stores
│   │   └── services/        # API сервисы
│   └── public/              # Статические файлы
├── docker/                  # Docker конфигурации
└── docs/                    # Документация
```

### Миграции базы данных

```bash
cd backend

# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1

# Просмотр истории миграций
alembic history
```

### Работа с базой данных

```bash
# Инициализация БД (создание таблиц)
python scripts/init_db.py --sync

# Проверка конфигурации
python scripts/init_db.py --check
```

## 👥 Роли пользователей

### 🏪 Кладовщик (warehouse_keeper)
- Приемка материалов от поставщиков
- Регистрация в системе
- Размещение на складе
- Первичная проверка документов

### 🔍 ОТК (quality_control)
- Визуальный контроль материалов
- Проверка соответствия спецификации
- Принятие решения о допуске к испытаниям
- Одобрение/отклонение материалов

### 🧪 ЦЗЛ - Разрушающий контроль (lab_destructive)
- Механические испытания на растяжение
- Испытания на ударную вязкость
- Испытания на твердость
- Химический анализ

### 🔬 ЦЗЛ - Неразрушающий контроль (lab_non_destructive)
- Ультразвуковой контроль
- Радиографический контроль
- Магнитопорошковый контроль
- Капиллярный контроль

### 🏭 Производство (production)
- Запрос материалов для производства
- Просмотр доступных материалов
- Подтверждение получения материалов
- Отчеты об использовании

### ⚙️ Администратор (administrator)
- Настройка workflow процессов
- Управление пользователями и ролями
- Настройка системы
- Просмотр всех данных

## 📊 Workflow материалов

```mermaid
graph LR
    A[RECEIVED] --> B[QUARANTINE]
    B --> C[TESTING]
    C --> D[APPROVED]
    D --> E[RELEASED]
    
    B --> F[REJECTED]
    C --> F
    D --> F
    
    F --> G[DISPOSED]
```

### Описание статусов:

| Статус | Описание | Ответственный |
|--------|----------|---------------|
| **RECEIVED** | Материал получен на склад | Кладовщик |
| **QUARANTINE** | На карантине, ожидает контроля | ОТК |
| **TESTING** | Проходит испытания | ЦЗЛ |
| **APPROVED** | Одобрен для использования | ОТК |
| **RELEASED** | Выдан в производство | Производство |
| **REJECTED** | Отклонен по результатам контроля | ОТК/ЦЗЛ |

## 🧪 Тестирование

### Backend тесты
```bash
cd backend

# Запуск всех тестов
pytest

# Запуск с покрытием кода
pytest --cov=src

# Запуск конкретного теста
pytest tests/test_materials.py -v
```

### Frontend тесты
```bash
cd frontend

# Запуск unit тестов
npm run test

# Запуск e2e тестов
npm run test:e2e
```

## 📝 API Документация

После запуска backend сервера документация доступна по адресам:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI схема**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Основные эндпоинты:

- `GET /api/v1/materials/` - Список материалов
- `POST /api/v1/materials/` - Создание материала
- `GET /api/v1/users/me` - Текущий пользователь
- `POST /api/v1/workflows/transition` - Изменение статуса

## 🔧 Конфигурация

### Backend (.env)
```env
# Основные настройки
APP_NAME="Metal Inspection System"
ENVIRONMENT=development
DEBUG=True

# База данных (выберите один вариант)
DATABASE_URL=sqlite:///./metal_inspection.db
# DATABASE_URL=postgresql://metal_user:metal_pass@localhost:5432/metal_inspection

# Безопасность
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Redis (опционально)
REDIS_URL=redis://localhost:6379

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env)
```env
# API URL
VITE_API_URL=http://localhost:8000

# Другие настройки
VITE_APP_TITLE="Metal Inspection System"
```

## 🚨 Устранение неполадок

### Частые проблемы:

1. **Ошибка подключения к БД**
   ```bash
   # Проверьте настройки в .env файле
   python scripts/init_db.py --check
   ```

2. **Ошибки миграций**
   ```bash
   # Сброс миграций (ОСТОРОЖНО!)
   alembic downgrade base
   alembic upgrade head
   ```

3. **Проблемы с зависимостями Python**
   ```bash
   # Переустановка зависимостей
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

4. **Проблемы с Frontend**
   ```bash
   # Очистка кеша и переустановка
   rm -rf node_modules package-lock.json
   npm install
   ```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции: `git checkout -b feature/new-feature`
3. Внесите изменения и добавьте тесты
4. Убедитесь, что все тесты проходят
5. Создайте Pull Request

### Стандарты кода:

- **Python**: PEP 8, используйте `black` для форматирования
- **JavaScript**: ESLint + Prettier
- **Commits**: Используйте conventional commits

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

При возникновении вопросов или проблем:

1. Проверьте [Issues](https://github.com/AndreySavastyuk/material-inspection2/issues)
2. Создайте новый Issue с подробным описанием
3. Обратитесь к документации в папке `docs/`

---

**Версия**: 1.0.0  
**Дата последнего обновления**: 17 августа 2025  
**Совместимость**: Python 3.13+, Node.js 18+
