from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from common.config import mysql_url

engine = create_engine(mysql_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# FastAPI dependency: yield a session and ensure close after request
# Note: Do NOT wrap with @contextmanager; FastAPI expects a generator function.
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()