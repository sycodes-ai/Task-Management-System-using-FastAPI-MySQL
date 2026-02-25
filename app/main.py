from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management System API",
    description="API for managing users and tasks",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):5173",
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Task Management System API. Visit /docs for documentation."}

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)
