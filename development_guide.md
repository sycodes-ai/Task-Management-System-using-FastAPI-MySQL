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
│   ├── database.py           # MySQL database connection and session management
│   ├── models.py             # SQLAlchemy ORM models (Database Tables)
│   ├── schemas.py            # Pydantic models (Data validation and serialization)
│   ├── auth.py               # Authentication and authorization logic (JWT, hashing)
│   ├── routers/              # API Route handlers
│   │   ├── __init__.py
│   │   ├── users.py          # Endpoints for user management (register, login)
│   │   └── tasks.py          # Endpoints for task management (CRUD operations)
│   ├── core/                 # Core configuration
│   │   ├── __init__.py
│   │   └── config.py         # Environment variables and app settings
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

### 3. Running the Application
To run the server locally for development:
```bash
uvicorn app.main:app --reload
```
The FastAPI instance is initialized in `app/main.py` which sets up:
- The `app` (FastAPI instance) with title and description.
- CORS Middleware allowing all origins for development.
- The `Root` entry point (`/`).
- Router inclusions for `/users` and `/tasks` from the `app.routers` package.

The API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and the root message at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Development Rules
- **No Git Usage**: This project is developed locally. Do not use git add, commit, or push. Ensure sensitive credentials remain strictly local.
- **Code Separation**: Keep database models (`models.py`) strictly separated from data validation schemas (`schemas.py`).
- **Feature Modules**: All new API features should be added as separate files in the `app/routers/` directory and then included in `main.py` via `app.include_router()`.
