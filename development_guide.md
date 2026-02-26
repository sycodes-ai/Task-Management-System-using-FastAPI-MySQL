# Task Management System - Development Guide

## Project Overview
This project is a **Task Management System** built using **FastAPI** and **MySQL**. 

## Project Structure
The folder structure follows standard FastAPI best practices for scalability and maintainability.

```text
Task Management System/
├── app/
│   ├── __init__.py           # Makes the app folder a Python package
│   ├── main.py               # FastAPI application instance and entry point
│   ├── models/               # SQLAlchemy ORM models (User, Task)
│   ├── schemas/              # Pydantic models (Data validation and serialization)
│   ├── crud/                 # CRUD operations
│   ├── db/                   # Database connection and session management
│   ├── core/                 # Core configuration (Security, config)
│   ├── api/                  # API Route handlers
│   │   ├── deps.py           # Dependency injections (get_db, get_current_user, get_current_admin)
│   │   └── api_v1/           # Versioned API routes
│   │       ├── api.py        # Central router aggregator
│   │       └── endpoints/    # Specific endpoint handlers (users.py, tasks.py, login.py)
├── my-react-app/             # React Frontend (Vite)
│   ├── src/
│   │   ├── components/       # Login, Register, Dashboard UI
│   │   ├── App.jsx           # React routing setup
│   │   ├── api.js            # Axios client configured for FastAPI
│   │   └── index.css         # Premium and responsive styling
│   ├── package.json          # Frontend dependencies
│   └── vite.config.js        # Vite build configuration
├── .env                      # Environment variables stored locally (not committed)
├── Pipfile                   # Pipenv dependencies
├── Pipfile.lock              # Pipenv lock file
└── development_guide.md      # Project documentation and guidelines
```

## Setup Instructions

### 1. Database Configuration
You will need a running instance of MySQL. In your root directory, create a `.env` file containing the connection string:
```ini
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Environment
The application dependencies are managed via `pipenv`. Make sure you have the required packages (like `fastapi`, `uvicorn`, `sqlalchemy`, `pymysql`, `passlib`, `python-jose`, and `python-dotenv`).

### 3. Database Connection & Sessions
The database connection is managed via `app/db/session.py` and `app/db/base_class.py`.
- Connects to MySQL using the `DATABASE_URL` environment variable.
- Provides `SessionLocal` for independent transactions.
- Provides the `get_db()` dependency mapping in `app/api/deps.py` for FastAPI injection.

**Example usage in route handlers:**
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db

@router.get("/")
def get_items(db: Session = Depends(get_db)):
    pass
```

### 4. Data Validation & Serialization
Data validation is handled via **Pydantic** in `app/schemas.py`.
- **Base Models**: Contain common attributes.
- **Create Models**: Inherit from Base and add required fields for creation (e.g., passwords).
- **Response Models**: Add IDs, timestamps, and relationships. They use `class Config: from_attributes = True` to parse SQLAlchemy ORM objects into JSON seamlessly.

### 5. Authentication (JWT) & Role-Based Access Control (RBAC)
The application secures endpoints using **OAuth2 with Password (and hashing), and Bearer with JWT tokens**, managed in `app/core/security.py` and `app/api/deps.py`.
- **Roles**: Users have an Enum `role` assigned as either `admin` or `staff`.
- **Dependency Map**: 
  - To protect a generic route, it requires `Depends(deps.get_current_user)`.
  - To protect an admin-only route, it requires `Depends(deps.get_current_admin)`.

### 6. Endpoint Routers
The application logically splits features into dedicated routers mapped inside `app/api/api_v1/api.py`.

**`Users` (`app/api/api_v1/endpoints/users.py`)**:
- `POST /register`: Registers a new user account (accepts a `role`).
- `GET /me`: Protected route returning the current authenticated user's profile.
- `GET /`: Protected route returning all users (Admin only).

**`Login` (`app/api/api_v1/endpoints/login.py`)**:
- `POST /login/access-token`: Generates an access token mapped to the `OAuth2PasswordRequestForm`.

**`Tasks` (`app/api/api_v1/endpoints/tasks.py`)**:
- Tasks have a `status` Enum (`pending`, `in_progress`, `completed`).
- `POST /tasks/`: Admin only endpoint. Creates a task and assigns it to a `staff` member (`assignee_id`).
- `GET /tasks/`: Admin sees all tasks. Staff members only see tasks assigned to them.
- `PUT /tasks/{task_id}`: Admin can update all fields (title, desc, status, assignee). Staff can only update the `status` field.
- `DELETE /tasks/{task_id}`: Admin only.

### 7. Running the Application
To run the server locally, you need to start both the FastAPI backend and the React frontend in parallel.

**Backend (FastAPI):**
```bash
# In the root project directory:
uvicorn app.main:app --reload
```
The FastAPI instance is initialized in `app/main.py` which sets up:
- The `app` (FastAPI instance) with title and description.
- CORS Middleware allowing all origins for development.
- The `Root` entry point (`/`).
- Router inclusions for `/users` and `/tasks` from the `app.routers` package.

The API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and the root message at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

**Frontend (React/Vite):**
```bash
# In a separate terminal, navigate to the frontend directory:
cd my-react-app
npm run dev
```
The frontend will typically run at `http://localhost:5173/` and communicates with the backend via the Axios client configured in `my-react-app/src/api.js`.

## Development Rules
- **No Git Usage**: This project is developed locally. Do not use git add, commit, or push. Ensure sensitive credentials remain strictly local.
- **Code Separation**: Keep database models (`models.py`) strictly separated from data validation schemas (`schemas.py`).
- **Feature Modules**: All new API features should be added as separate files in the `app/routers/` directory and then included in `main.py` via `app.include_router()`.
