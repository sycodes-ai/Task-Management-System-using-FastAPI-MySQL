# Task Management System

[![CI](https://github.com/sycodes-ai/Task-Management-System-using-FastAPI-MySQL/actions/workflows/ci.yml/badge.svg)](https://github.com/sycodes-ai/Task-Management-System-using-FastAPI-MySQL/actions/workflows/ci.yml)

CI runs the tests against SQLite and MySQL 8 and smoke-tests the Docker image.

A full-stack task manager with JWT authentication and role-based access control: admins create and assign tasks, staff update the status of the tasks assigned to them. Built with **FastAPI**, **SQLAlchemy** and **React**.

## 🌐 Live demo

**https://task-management-system-using-fastapi.onrender.com**

Log in with the demo accounts below, or click **Log in as Admin** / **Log in as Staff** on the login page. (Log in with the **email**, not the username.)

| Role | Email | Password | Username |
| :--- | :--- | :--- | :--- |
| Admin | `admin@demo.com` | `Admin123!` | `demo_admin` |
| Staff | `staff@demo.com` | `Staff123!` | `demo_staff` |
| Staff | `alex@demo.com` | `Staff123!` | `alex` |

> The demo runs on free hosting, which goes to sleep when idle: **the first load can take 30–60 seconds**. The demo accounts are public, so don't enter real data. Changes made in the demo may be reset when the service restarts.

### Screenshots

**Admin dashboard**

![Admin dashboard](docs/admin-dashboard.png)

**Staff dashboard**

![Staff dashboard](docs/staff-dashboard.png)

## ✨ Features

- **JWT authentication**: register, log in, and call the API with a Bearer token that expires (30 minutes by default).
- **Role-based access control (RBAC)**, enforced on the server:

  | | Admin | Staff |
  | :--- | :---: | :---: |
  | See tasks | all tasks | only tasks assigned to them |
  | Create and assign tasks | ✅ | ❌ |
  | Edit title, description, assignee | ✅ | ❌ |
  | Change task status | ✅ | ✅ (own tasks only) |
  | Delete tasks | ✅ | ❌ |
  | List users | ✅ | ❌ |

- **Task statuses**: `pending`, `in_progress`, `completed`.
- **Filtering and search**: filter by status (admins also by assignee), case-insensitive search in title and description, sort by creation date.
- **Pagination**: 20 tasks per page by default (1–100), with the total count in the `X-Total-Count` header. The UI has Previous / Next buttons.
- **Stats**: task counts per status, shown as cards on both dashboards.
- **Validation**: Pydantic checks every request (lengths, allowed statuses, email format) and returns `422` for bad input.
- **Demo mode**: `DEMO_MODE=true` creates the demo users and tasks on an empty database.
- **One deployable service**: FastAPI serves the React build, so a single container runs the whole app.

## 🛠️ Tech stack

| Area | Technology |
| :--- | :--- |
| Backend | Python, FastAPI, SQLAlchemy 2, Pydantic v2 |
| Auth | JWT (`python-jose`), bcrypt (`passlib`), OAuth2 password flow |
| Database | MySQL (`pymysql`), PostgreSQL (`psycopg`) or SQLite, chosen with `DATABASE_URL` |
| Frontend | React 19, Vite, React Router, Axios |
| Tests | pytest, httpx (FastAPI TestClient) |
| Delivery | Docker (multi-stage), Docker Compose, GitHub Actions |

## 🏗️ Architecture

Every request goes through the same layers:

```text
Browser (React)
   │  HTTP  /api/v1/...
   ▼
Router        app/api/api_v1/endpoints/   validates input with Pydantic schemas
   │  Depends(...)
   ▼
Dependencies  app/api/deps.py             get_db · get_current_user (JWT → user, 401) · get_current_admin (403)
   ▼
CRUD          app/crud/                   queries and writes, no HTTP code
   ▼
Database      app/models/ + app/db/       SQLAlchemy models; MySQL, PostgreSQL or SQLite
```

- **Separation of concerns**: route handlers decide *who may do what*; the CRUD layer only talks to the database.
- **Dependency injection**: database sessions, authentication and role checks are FastAPI dependencies, so tests can replace them.
- **One service**: `app/core/frontend.py` serves `my-react-app/dist` (or `STATIC_DIR`) and returns `index.html` for unknown non-API paths, so React Router works on refresh. API routes, `/docs` and unknown `/api/...` paths (JSON 404) are never replaced by the React page.

### Project structure

```text
app/
├── api/
│   ├── api_v1/
│   │   ├── endpoints/   # login, users, tasks, health
│   │   └── api.py       # router aggregator
│   └── deps.py          # get_db, get_current_user, get_current_admin
├── core/
│   ├── config.py        # settings from environment variables
│   ├── security.py      # password hashing, JWT creation
│   └── frontend.py      # serves the React build
├── crud/                # database operations (users, tasks, filters, stats)
├── db/
│   ├── session.py       # engine for MySQL / PostgreSQL / SQLite
│   └── seed.py          # demo users and tasks
├── models/              # SQLAlchemy models (User, Task)
├── schemas/             # Pydantic schemas
└── main.py              # create_app(), lifespan (create tables, seed)
my-react-app/            # React (Vite) frontend
tests/                   # pytest suite
Dockerfile · docker-compose.yml · .github/workflows/ci.yml
```

## ⚙️ Run locally

### 1. Configuration

Settings come from environment variables or a `.env` file in the project root. Everything has a default, so the app starts with no configuration at all (SQLite file `tasks.db`). To use MySQL:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/db_name
SECRET_KEY=a-long-random-string
```

[`.env.example`](.env.example) lists every variable with a comment. Never commit your real `.env`.

### 2. Backend

Pipenv (the `Pipfile` asks for Python 3.13):

```bash
pipenv install
pipenv run uvicorn app.main:app --reload
```

or a plain virtual environment (Python 3.12+):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tables are created on start-up. Add `DEMO_MODE=true` to also create the demo users and tasks. The API is at http://127.0.0.1:8000 and the interactive docs at http://127.0.0.1:8000/docs.

### 3. Frontend dev server

```bash
cd my-react-app
npm ci
npm run dev
```

Open http://localhost:5173. In development, Vite forwards `/api` requests to `http://127.0.0.1:8000`, so start the backend first. `npm run build` creates `my-react-app/dist`; when it exists, FastAPI serves it at http://127.0.0.1:8000 and you don't need the dev server.

### 4. Docker

Everything with MySQL, using Docker Compose:

```bash
docker compose up --build
```

Open http://localhost:8000. This starts `mysql:8` and the app with `DEMO_MODE=true`.

Only the app image (SQLite):

```bash
docker build -t tms .
docker run -p 8000:8000 -e DEMO_MODE=true -e SECRET_KEY=change-me tms
```

## ✅ Tests

```bash
pip install -r requirements-dev.txt
pytest
```

- **92 tests** run anywhere: they use an in-memory SQLite database and ignore your `.env`. They cover registration, login, token errors, role rules, validation, filters, pagination, stats, the demo seed and serving the React build.
- **1 more test** (93 in total) runs a short end-to-end flow on a real database. It is skipped unless `TEST_DATABASE_URL` is set. **CI runs it against a MySQL 8 service.** To run it yourself, use an empty throwaway database (its tables are dropped afterwards):

  ```bash
  TEST_DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/tms_test pytest
  ```

- **CI** (GitHub Actions) runs the tests, `npm run lint` and `npm run build`, then builds the Docker image and smoke-tests it.

## 🔌 API endpoints (v1)

Base path: `/api/v1`. Interactive documentation: `/docs`.

### Users, auth and health

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| **POST** | `/users/register` | Register a user. Always creates a **staff** account; a `role` in the body is ignored. | Public |
| **POST** | `/login/access-token` | Log in (form fields `username` = email, `password`) and receive a JWT. | Public |
| **GET** | `/users/me` | Current user profile. | Any logged-in user |
| **GET** | `/users/` | List users. Query: `skip` (≥ 0), `limit` (1–100, default 100). | **Admin** |
| **GET** | `/health` | `{"status": "ok"}` (no database call). Used by the hosting health check. | Public |

### Tasks

| Method | Endpoint | Description | Role rules |
| :--- | :--- | :--- | :--- |
| **GET** | `/tasks/` | List tasks. Query: `status`, `assignee_id`, `q`, `skip` (≥ 0), `limit` (1–100, default 20), `sort` (`-created_at` default, or `created_at`). Total in the `X-Total-Count` header. | Admin: all tasks (`assignee_id` filter allowed). Staff: own tasks only (`assignee_id` is ignored). |
| **GET** | `/tasks/stats` | Counts per status: `pending`, `in_progress`, `completed`, `total`. | Admin: all tasks. Staff: own tasks. |
| **GET** | `/tasks/{id}` | Get one task. | Admin: any. Staff: own only (`403` otherwise). |
| **POST** | `/tasks/` | Create and assign a task. `404` if the assignee does not exist. | **Admin only** |
| **PUT** | `/tasks/{id}` | Update a task. | Admin: all fields. Staff: own task, `status` only (`403` if they change anything else, `422` if `status` is missing). |
| **DELETE** | `/tasks/{id}` | Delete a task (`204`). | **Admin only** |

### Status codes

| Code | Meaning |
| :--- | :--- |
| `400` | Wrong email or password, or the email/username is already registered |
| `401` | Missing, invalid or expired token (with `WWW-Authenticate: Bearer`), or the user no longer exists or was deactivated |
| `403` | Logged in, but not allowed (for example staff calling an admin endpoint) |
| `404` | Task or assignee not found; unknown API paths return a JSON 404 |
| `422` | Invalid input (for example an unknown `status`, a short password, `limit=500`) |

## 🔑 Authentication flow

1. A user registers at `/users/register` (always as staff) or uses a demo account.
2. The user sends email and password to `/login/access-token`.
3. The server returns a **JWT** that identifies the user and expires after `ACCESS_TOKEN_EXPIRE_MINUTES` (30 by default).
4. The client sends it as `Authorization: Bearer <token>`.
5. On every request, the `get_current_user` dependency verifies the signature and expiry and loads the user (`401` if that fails). Role checks then return `403` when the action is not allowed.

## 🔒 Security notes

- **Passwords** are hashed with bcrypt and never returned by the API.
- **Registration is always staff.** The client cannot choose a role; admins are created only by the demo seed or directly in the database.
- **Tokens** are signed with `SECRET_KEY` and expire. In production (`ENVIRONMENT=production`) the app refuses to start without a `SECRET_KEY`; in development a random one is generated.
- **Authorization is checked on the server**, not only in the UI: staff can only read their own tasks and can only change a task's status, even if they call the API directly.
- **401 and 403 are different**: 401 means "log in again", 403 means "you are logged in but not allowed".
- **Input is validated** with Pydantic, assignees are checked, and all queries go through the SQLAlchemy ORM (search text is escaped).
- **CORS** is limited to `CORS_ORIGINS` and is not needed when FastAPI serves the frontend.
- **Secrets come from environment variables.** `.env` is gitignored, `.env.example` has placeholders only, the Docker image excludes `.env`, and the container runs as a non-root user.
- The demo accounts are public on purpose and are meant for the demo only.

## 🚧 Limitations and next steps

- **No database migrations.** Tables are created on start-up if they are missing; changing the schema later needs [Alembic](https://alembic.sqlalchemy.org/).
- **No refresh tokens.** There is one short-lived access token, stored in the browser's `localStorage`; tokens cannot be revoked.
- **No rate limiting on login**, so repeated password guesses are not slowed down.
- **No audit log** of who changed what.
- **Admins cannot be created in the app.** Outside demo mode, promote a user in the database: `UPDATE users SET role = 'admin' WHERE email = '...';`.
- **PostgreSQL** is supported through `DATABASE_URL`, but the tests run against SQLite and MySQL, not PostgreSQL.
- **No automated frontend tests** (the frontend is checked with lint and build only).

Next steps: Alembic migrations, refresh-token rotation, login rate limiting, an audit log.

## 📄 License

This project is licensed under the MIT License.
