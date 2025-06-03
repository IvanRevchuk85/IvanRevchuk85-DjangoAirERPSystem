# 🛡️ FastAPI Auth Service

Powerful authentication microservice on **FastAPI** with support for:
- JWT (access + refresh)
- roles (user / admin)
- blocking and soft delete
- password change
- logging
- test coverage and running in Docker
---

## 🚀 Functionality

- ✅ Registration
- ✅ Login by email and password
- ✅ Access token update (refresh)
- ✅ Password change
- ✅ Getting profile
- ✅ Getting and changing balance
- ✅ Soft delete (soft-delete)
- ✅ Blocking users
- ✅ Roles `admin`, `user` + access restrictions
- ✅ CLI commands init/drop DB
- ✅ PostgreSQL, Alembic migrations
- ✅ Unit + integration tests
- ✅ Docker + Docker Compose

---

## 📁 Project structure

```
task_21/
├── alembic/                            # Catalog for Alembic - DB Migration Management
│   ├── env.py                          # Alembic to SQLAlchemy Connection Configuration
│   ├── README                          # Alembic documentation 
│   ├── script.py.mako                  # Template for autogenerating migrations
│   └── versions/                       # Migration files are stored
│       ├── 422fdcb18e36_create_users...   
│       ├── 96fa7ea6e3d1_add_role_is_...  
│       └── cba0f28fc244_add_role_fiel...  

├── docs/
│   └── diagramms/                      # Architecture Diagrams
│       ├── Blank diagram.png           # Scheme
│       └── README.md                   # Description of the diagrams

├── fastapi_auth_service/              # Main application code
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py             # Package initialization
│   │   │   ├── dependencies.py         # Common dependencies (eg current_user)
│   │   │   ├── redis.py                # Connecting to Redis (refresh token storage)
│   │   │   └── settings.py             # 
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py                 # User model (SQLAlchemy)
│   │   ├── repositories/
│   │   │   └── user.py                 # CRUD-DB operations for User
│   │   ├── routers/
│   │   │   ├── admin_routes.py         # Admin endpoints (block/unblock, get users, etc.)
│   │   │   ├── auth_routers.py         # Authentication endpoints
│   │   │   └── user_routers.py         # User endpoints 
│   │   ├── schemas/
│   │   │   └── user.py                 # Pydantic schemes 
│   │   ├── services/
│   │   │   ├── auth_service.py         # Business logic: registration, login, password change
│   │   │   └── token_cache.py          # Working with Redis and refresh tokens
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── security.py             # JWT tokens, password hashing
│   │   ├── database.py                 # Connecting to PostgreSQL via async SQLAlchemy
│   │   ├── logging_config.py           # Logging 
│   │   └── main.py                     # Entry point: FastAPI application
│   │  
│   tests/                              # Catalog with tests
│   ├── unit/                           # Unit tests
│   │   ├── test_auth_service.py        # Authorization business logic tests
│   │   ├── test_dependecies.py         # Dependency tests (is_admin, is_user)
│   │   ├── test_logging_config.py      # Logging tests
│   │   ├── test_security.py            # JWT, hashing and password validation tests
│   │   ├── test_token_cache.py         # Token Caching Tests
│   │   ├── test_user_crud.py           # Tests of CRUD operations with User
│   │   └── test_user_schemas.py        # Pydantic Scheme Tests
│   ├── conftest.py                     # Fixtures: async_client, registered_user, etc.
│   ├── db_waiter.py                    # Waiting for PostgreSQL database to start (in docker)
│   ├── test_admin_routes.py            # Test admin
│   ├── test_login.py                   # Login integration tests, refresh, logout
│   ├── test_me.py                      # Test getting current user
│   ├── test_register.py                # Registration tests (including duplicates)
│   ├── test_change_password.py         # Password change test
│   └── __init__.py                     # Package initialization

├── cli.py                               # CLI commands (create/delete DB)

# Корневые файлы
├── .env                                 # Environment variables (.env)
├── .gitignore                           # Ignored files git
├── alembic.ini                          # Configuration Alembic
├── docker-compose.yml                   # Docker build: FastAPI + PostgreSQL
├── Dockerfile                           # Container assembly instructions FastAPI
├── pytest.ini                           # Settings pytest 
├── README.md                            # Project documentation
└── requirements.txt                     # Project Dependencies

```

---

## ⚙️ Install and run

### 🔧 Installing dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 🚀 Launching the application

```bash
uvicorn fastapi_auth_service.app.main:app --reload
```

FastAPI will be available at:
👉 http://127.0.0.1:8000

### 🔍 Swagger documentation

👉 http://127.0.0.1:8000/docs

---

## 🧪 Testing

### 📦 Running tests with coverage

```bash
pytest --cov=fastapi_auth_service --cov-report=term-missing -v
```

### ✅ Coverage

- Overall level: **85%**
- Tests for registration, login, refresh, password change, profile
- Checking blocking, soft delete, roles
- Unit and integration tests (httpx + fixtures)

---

## 🐳 Docker

### 🔨 Build and launch

```bash
docker-compose up --build
```

Will start:
- `web` — FastAPI application
- `db` — PostgreSQL (в Docker)

The application will be available on [http://localhost:8000](http://localhost:8000)

---

## 🔌 CLI commands

```bash
# Initialize DB
python fastapi_auth_service/cli.py init-db

# Delete DB
python fastapi_auth_service/cli.py drop-db
```

---

## 🔐 Endpoints

| Method | Path | Description |
|-------|------|---------|
| `POST` | `/auth/register` | Registration |
| `POST` | `/auth/login` | Login (access + refresh) |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/change-password` | Change password |
| `GET` | `/users/me` | Get profile |
| `GET/PUT` | `/users/balance` | Get / update balance |
| `GET` | `/users/` | (admin) All users with filters |
| `GET` | `/users/deleted` | (admin) Deleted users |
| `POST` | `/admin/block/{id}` | (admin) Block |
| `POST` | `/admin/unblock/{id}` | (admin) Unblock |
| `GET` | `/admin/check` | Check admin rights |

---

## 🧠 Technologies used

- **FastAPI** — API framework
- **Pydantic v2** — strong validation
- **PostgreSQL** — database
- **SQLAlchemy (async)** — ORM
- **Alembic** — database migrations
- **passlib[bcrypt]** — password hashing
- **PyJWT** — access tokens
- Redis — temporary storage of refresh tokens
- **httpx + pytest-asyncio** — testing
- **Docker + Docker Compose**
---

## 👨‍🎓 Author

**Ivan Revchuk** 
Project as part of the training course **Python Web Developer (foxminded.ua)**

Mentor: **Victor Kovtun**

---

## 📜 License

The project is licensed under the [MIT License](https://opensource.org/licenses/MIT)