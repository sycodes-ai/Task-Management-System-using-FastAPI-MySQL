from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def normalize_database_url(url: str) -> str:
    """Use the psycopg 3 driver for PostgreSQL URLs (Render, Neon and Heroku use postgres://)."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url

def create_db_engine(url: str, **kwargs) -> Engine:
    """Create an engine for MySQL, PostgreSQL or SQLite with the settings each one needs."""
    url = normalize_database_url(url)
    connect_args = {}
    if url.startswith("sqlite"):
        # FastAPI runs sync endpoints in a thread pool
        connect_args["check_same_thread"] = False
    return create_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600,
        **kwargs
    )

engine = create_db_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
