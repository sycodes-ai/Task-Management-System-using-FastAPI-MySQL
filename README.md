# Task Management System API

A professional, modular, and scalable Task Management System built with **FastAPI**, **MySQL**, and **React**. This project implements **Role-Based Access Control (RBAC)**, allowing administrators to manage and assign tasks to staff members.

## 🚀 Project Overview
The Task Management System is designed for team-based productivity. 
- **Admins**: Can manage all users, create tasks, and assign them specifically to Staff members. Admins have full editing rights over all tasks.
- **Staff**: Can view their personal task lists and update the progress status of their assigned work.
- **Task Statuses**: Supports a robust lifecycle — `Pending`, `In Progress`, and `Completed`.

## 🛠️ Technology Stack
- **Language**: Python 3.13
- **Framework**: FastAPI (Asynchronous API)
- **Database**: MySQL (using SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Tokens) with OAuth2 Password Bearer
- **Validation**: Pydantic v2
- **Environment**: Pipenv for dependency management
- **Frontend**: React (Vite-based)

## 🏗️ Architecture & Design Principles
The project follows **Clean Architecture** principles to ensure the codebase remains maintainable and testable:

- **RBAC Implemented**: Native support for `admin` and `staff` roles within the JWT claims and database models.
- **Modularity**: Logic is split into dedicated packages (`models`, `schemas`, `crud`, `api`, `core`).
- **Separation of Concerns**: Database logic (CRUD) is decoupled from API route handlers.
- **Dependency Injection**: Utilizes FastAPI's dependency system for database sessions, authentication, and role authorization.
- **Secure by Design**: Password hashing with Bcrypt and stateless JWT-based authentication.

## 📂 Project Structure
```text
app/
├── api/
│   ├── api_v1/          # Versioned API routes (v1)
│   │   ├── endpoints/   # Individual route handlers (login, users, tasks)
│   │   ├── api.py       # Main router aggregator
│   │   └── deps.py      # Common dependencies (get_db, get_current_user, get_current_admin)
├── core/                # Global config (Security, JWT)
├── crud/                # Encapsulated database operations (CRUD layer)
├── db/                  # Session management and base classes
├── models/              # SQLAlchemy database models (User, Task)
├── schemas/             # Pydantic data validation schemas
└── main.py              # Application entry point
```

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.12+
- MySQL Server
- Pipenv (`pip install pipenv`)

### 1. Environment Configuration
Create a `.env` file in the root directory and configure your variables:
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/db_name
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Backend Setup
```bash
# Install dependencies
pipenv install

# Initialize database (tables are created on startup)
pipenv run uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd my-react-app
npm install
npm run dev
```

## 🔌 API Endpoints (v1)

### Users & Auth
| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/users/register` | Register a new user (with role) | None |
| **POST** | `/api/v1/login/access-token` | Login and receive JWT | None |
| **GET** | `/api/v1/users/me` | Get current user profile | Any |
| **GET** | `/api/v1/users/` | List all users | **Admin** |

### Tasks
| Method | Endpoint | Description | Role Restrictions |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/tasks/` | List tasks | Admin: All, Staff: Assigned only |
| **POST** | `/api/v1/tasks/` | Create & assign task | **Admin only** |
| **PUT** | `/api/v1/tasks/{id}` | Update task | Admin: Full edit, Staff: Status only |
| **DELETE** | `/api/v1/tasks/{id}` | Delete a task | **Admin only** |

## 🔑 Authentication Flow
1. User registers via `/register` selecting an `admin` or `staff` role.
2. User provides credentials to `/login/access-token`.
3. Server returns a **JWT Access Token** including the user ID.
4. User includes this token in the `Authorization: Bearer <token>` header.
5. The API enforces role-based permissions on a per-request basis.

## 🔮 Future Improvements
- [ ] Implement Alembic for database migrations.
- [ ] Add unit and integration tests using `pytest`.
- [ ] Implement Refresh Token rotation.
- [ ] Dockerize the entire application (docker-compose).
- [ ] Add CI/CD pipelines (GitHub Actions).

## 📄 License
This project is licensed under the MIT License.