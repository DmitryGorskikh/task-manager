cat > README.md << 'EOF'
# Task Manager API

Production-ready REST API built with FastAPI, async SQLAlchemy, and PostgreSQL.

## Tech Stack

- **FastAPI** — async web framework
- **SQLAlchemy 2.0** — async ORM
- **PostgreSQL** — database
- **Alembic** — migrations
- **JWT** — authentication
- **Docker** — containerization
- **pytest** — async tests

## Features

- JWT authentication (access + refresh tokens)
- Projects and Tasks CRUD
- Task filtering by status, priority, project
- Pagination
- Centralized error handling
- Structured logging

## Quick Start

```bash
# Clone the repo
git clone https://github.com/DmitryGorskikh/task-manager.git
cd task-manager

# Copy env file
cp .env.example .env

# Start with Docker
docker compose up --build

# Run migrations
docker exec task_manager_app alembic upgrade head
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Register |
| POST | /api/v1/auth/login | Login |
| POST | /api/v1/auth/refresh | Refresh token |
| GET | /api/v1/users/me | Current user |
| CRUD | /api/v1/projects | Projects |
| CRUD | /api/v1/tasks | Tasks |

## Run Tests

```bash
pytest tests/ -v
```

## Docs

Swagger UI available at `http://localhost:8000/docs`
EOF