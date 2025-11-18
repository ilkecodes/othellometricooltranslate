# lgs-platform

A FastAPI-based adaptive learning platform for LGS (Liselere Giriş Sınavı) exam preparation. Includes student exams, teacher tools, and admin dashboard.

## Project Structure

```
lgs-platform/
├─ backend/           # FastAPI application
│  ├─ app/
│  │  ├─ main.py     # FastAPI entry point
│  │  ├─ core/       # Configuration, security, logging
│  │  ├─ api/v1/     # API routers (auth, student, teacher, admin, curriculum, questions)
│  │  ├─ models/     # SQLAlchemy ORM models
│  │  ├─ schemas/    # Pydantic request/response schemas
│  │  ├─ services/   # Business logic (adaptive engine, stats)
│  │  ├─ db/         # Database session and initialization
│  │  └─ utils/      # Utility functions (pagination, etc.)
│  ├─ migrations/    # Alembic database migrations
│  ├─ requirements.txt
│  ├─ .env.example
│  └─ alembic.ini
└─ frontend/         # Next.js application (TODO)
```

## Backend Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+ (or SQLite for local dev)
- pip/venv

### Installation

1. **Clone and navigate to backend**
   ```bash
   cd lgs-platform/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and JWT secret
   ```

5. **Initialize database (optional for local SQLite dev)**
   ```bash
   python -c "from app.db.init_db import init_db; init_db()"
   ```

6. **Run migrations (with Postgres)**
   ```bash
   alembic upgrade head
   ```

7. **Start development server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## Docker Setup

To run with Docker Compose (includes Postgres):

```bash
docker-compose up --build
```

This starts:
- Backend API on `http://localhost:8000`
- PostgreSQL on `localhost:5432`

## Authentication

The API uses JWT bearer tokens for authentication.

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "full_name": "John Doe",
    "password": "securepassword123"
  }'
```

### Login and get token
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student@example.com&password=securepassword123"
```

### Use token in requests
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/student/me
```

## Key Endpoints

- **Auth**
  - `POST /api/v1/auth/register` — Register new user
  - `POST /api/v1/auth/token` — Login and get JWT token
  - `GET /api/v1/auth/me` — Get current user info

- **Student**
  - `GET /api/v1/student/me` — Get student profile
  - `GET /api/v1/student/dashboard` — Get dashboard with stats (TODO)

- **Curriculum**
  - `GET /api/v1/curriculum` — List subjects and curriculum structure
  - `POST /api/v1/curriculum` — Create new curriculum item (admin)

- **Questions**
  - `GET /api/v1/questions` — List questions
  - `POST /api/v1/questions` — Create question (teacher/admin)

- **Exams**
  - `POST /api/v1/student/exams/start` — Start a new exam
  - `POST /api/v1/student/exams/{id}/answer` — Submit answer
  - `POST /api/v1/student/exams/{id}/finish` — Complete exam

## Database Migrations

Using Alembic for schema management:

```bash
# Create a new migration (auto-detect changes)
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Revert to previous version
alembic downgrade -1
```

## Development Notes

### Code Quality
- Pydantic v2 schemas with `model_config = {"from_attributes": True}` for ORM serialization
- Synchronous SQLAlchemy (sync engine) with PostgreSQL driver `psycopg2`
- JWT tokens with bcrypt password hashing
- Error handling with proper HTTP status codes and rollback on DB errors

### Performance Considerations
- Add database indexes on frequently queried columns (done in migrations)
- Avoid N+1 queries with `joinedload()` and `selectinload()`
- Cache question pools and student models (TODO)
- Use background workers for scoring and stats aggregation (TODO)

### Security
- Never commit `.env` with real secrets; use environment variables or secrets manager
- Change `JWT_SECRET_KEY` in production
- Restrict `CORS allow_origins` in production
- Add rate limiting for sensitive endpoints (TODO)
- Implement audit logging (TODO)

## Frontend (TODO)

Next.js app for student/teacher/admin dashboards. Planned structure:
- `/app/student/dashboard` — Student exam and progress dashboard
- `/app/student/exams/[id]` — Exam interface
- `/app/teacher/dashboard` — Teacher tools
- `/app/admin/dashboard` — Admin panel

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test with `uvicorn app.main:app --reload`
3. Run migrations if schema changed: `alembic revision --autogenerate -m "..."`
4. Commit and push: `git commit -m "feat: describe changes"` and `git push`
5. Open a pull request

## License

MIT

## Support

For issues or questions, open an issue on GitHub or contact the team.

