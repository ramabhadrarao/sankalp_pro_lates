from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from common.db.mysql import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), nullable=True)
    organization = Column(String(150), nullable=True)
    role = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    tier = Column(String(50), nullable=False, default="Starter")
    verified = Column(Boolean, default=False)
    locked_fields_after = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())