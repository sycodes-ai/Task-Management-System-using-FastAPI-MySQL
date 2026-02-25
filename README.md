# Task Management System API

A professional, modular, and scalable Task Management System built with **FastAPI**, **MySQL**, and **React**. This project demonstrates a clean architecture approach, prioritizing separation of concerns, data validation, and secure authentication.

## 🚀 Project Overview
The Task Management System is designed to help users efficiently manage their daily tasks. It provides a robust backend API for user registration, secure authentication, and full CRUD (Create, Read, Update, Delete) operations for tasks, each linked to a specific user.

## 🛠️ Technology Stack
- **Language**: Python 3.13
- **Framework**: FastAPI (Asynchronous API)
- **Database**: MySQL (using SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Tokens) with OAuth2 Password Bearer
- **Validation**: Pydantic v2
- **Environment**: Pipenv for dependency management
- **Frontend**: React (Vite-based)

## 🏗️ Architecture & Design Principles
The project follows **Clean Architecture** principles to ensure the codebase remains maintainable and testable as it grows:

- **Modularity**: Logic is split into dedicated packages (models, schemas, crud, api).
- **Separation of Concerns**: Database logic (CRUD) is decoupled from API route handlers.
- **Dependency Injection**: Utilizes FastAPI's dependency system for database sessions and authentication.
- **Data Validation**: Strict typing and validation using Pydantic models.
- **Secure by Design**: Password hashing with Bcrypt and stateless JWT-based authentication.

## 📂 Project Structure
```text
app/
├── api/
│   └── api_v1/          # Versioned API routes (v1)
│       ├── endpoints/   # Individual route handlers (login, users, tasks)
│       ├── api.py       # Main router aggregator
│       └── deps.py      # Common dependencies (get_db, get_current_user)
├── core/                # Global config and security utilities
├── crud/                # Encapsulated database operations (CRUD layer)
├── db/                  # Session management and base classes
├── models/              # SQLAlchemy database models
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
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/users/register` | Register a new user | No |
| **POST** | `/api/v1/login/access-token` | Login and receive JWT | No |
| **GET** | `/api/v1/users/me` | Get current user profile | Yes |
| **GET** | `/api/v1/tasks/` | List all tasks for current user | Yes |
| **POST** | `/api/v1/tasks/` | Create a new task | Yes |
| **PUT** | `/api/v1/tasks/{id}` | Update a specific task | Yes |
| **DELETE** | `/api/v1/tasks/{id}` | Delete a specific task | Yes |

## 🔑 Authentication Flow
1. User registers via `/register`.
2. User provides credentials to `/login/access-token`.
3. Server returns a **JWT Access Token**.
4. User includes this token in the `Authorization: Bearer <token>` header for protected requests.

## 🔮 Future Improvements
- [ ] Implement Alembic for database migrations.
- [ ] Add unit and integration tests using `pytest`.
- [ ] Implement Refresh Token rotation.
- [ ] Dockerize the entire application (docker-compose).
- [ ] Add CI/CD pipelines (GitHub Actions).

## 📄 License
This project is licensed under the MIT License.