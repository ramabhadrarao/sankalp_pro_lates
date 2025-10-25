from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from common.config import mysql_url

engine = create_engine(mysql_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

@contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()