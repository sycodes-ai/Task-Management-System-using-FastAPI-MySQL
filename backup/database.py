from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create SQLAlchemy engine
# pool_pre_ping checks the connection before using it (useful for MySQL)
# pool_recycle recycles connections to prevent them from becoming stale
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create SessionLocal class factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy declarative models
Base = declarative_base()

# Dependency to get Db session in FastAPI routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
