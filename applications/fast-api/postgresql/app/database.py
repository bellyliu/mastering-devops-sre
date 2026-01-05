from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings
import redis

settings = get_settings()

# PostgreSQL Database
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Redis Connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """Dependency for getting Redis client"""
    return redis_client
