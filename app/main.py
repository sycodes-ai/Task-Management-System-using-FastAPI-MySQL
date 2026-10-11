from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.seed import seed_demo_data
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    if settings.DEMO_MODE:
        with SessionLocal() as db:
            seed_demo_data(db)
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="Task Management System API",
        description="API for managing users and tasks",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS (Cross-Origin Resource Sharing)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
        expose_headers=["X-Total-Count"],
    )

    @app.get("/", tags=["Root"])
    def root():
        return {"message": "Welcome to the Task Management System API. Visit /docs for documentation."}

    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app

app = create_app()
