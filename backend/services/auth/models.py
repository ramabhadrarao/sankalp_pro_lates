from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from common.db.mysql import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), unique=True, index=True, nullable=True)
    organization = Column(String(255), nullable=True)
    role = Column(String(50), nullable=True)  # e.g., admin, advisor
    password_hash = Column(String(255), nullable=False)
    tier = Column(String(50), default="free")
    verified = Column(Boolean, default=False)
    locked_fields_after = Column(DateTime, nullable=True)
    user_type = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    terms_accepted = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(64), nullable=True)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String(256), unique=True, nullable=False)
    revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)

class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String(128), unique=True, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String(128), unique=True, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)