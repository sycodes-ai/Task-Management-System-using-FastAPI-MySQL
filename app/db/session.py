from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def normalize_database_url(url: str) -> str:
    """Use the psycopg 3 driver for PostgreSQL URLs (Render, Neon and Heroku use postgres://)."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url

database_url = normalize_database_url(settings.DATABASE_URL)

connect_args = {}
if database_url.startswith("sqlite"):
    # FastAPI runs sync endpoints in a thread pool
    connect_args["check_same_thread"] = False

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
