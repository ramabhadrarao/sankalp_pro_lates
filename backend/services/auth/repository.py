from sqlalchemy.orm import Session
from sqlalchemy import select, update
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from secrets import token_urlsafe

from common.config import REFRESH_EXPIRES_MINUTES
from .models import User, RefreshToken, EmailVerification, PasswordResetToken

# Use a hashing scheme that avoids bcrypt backend issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)

def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)

def create_user(db: Session, **data) -> User:
    password_hash = pwd_context.hash(data.pop("password"))
    if not data.get("locked_fields_after"):
        data["locked_fields_after"] = datetime.utcnow() + timedelta(hours=72)
    user = User(
        password_hash=password_hash,
        **data,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

# Refresh token management

def create_refresh_token(db: Session, user_id: int, token: str | None = None) -> RefreshToken:
    token_value = token or token_urlsafe(64)
    expires = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_EXPIRES_MINUTES)
    rt = RefreshToken(user_id=user_id, token=token_value, expires_at=expires)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

def revoke_refresh_tokens_for_user(db: Session, user_id: int):
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked == False).update({RefreshToken.revoked: True})
    db.commit()


def get_valid_refresh_token(db: Session, token: str) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.token == token, RefreshToken.revoked == False)
    rt = db.scalar(stmt)
    if not rt:
        return None
    if rt.expires_at < datetime.now(timezone.utc):
        return None
    return rt

# Email verification

def create_verification_token(db: Session, user_id: int) -> EmailVerification:
    v = EmailVerification(user_id=user_id, token=token_urlsafe(32))
    db.add(v)
    db.commit()
    db.refresh(v)
    return v

def mark_verification_used(db: Session, token: str) -> User | None:
    stmt = select(EmailVerification).where(EmailVerification.token == token, EmailVerification.used == False)
    v = db.scalar(stmt)
    if not v:
        return None
    v.used = True
    user = db.get(User, v.user_id)
    user.verified = True
    db.commit()
    return user

# Password reset

def create_password_reset_token(db: Session, user_id: int) -> PasswordResetToken:
    pr = PasswordResetToken(user_id=user_id, token=token_urlsafe(32))
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr

def consume_password_reset_token(db: Session, token: str, new_password: str) -> bool:
    stmt = select(PasswordResetToken).where(PasswordResetToken.token == token, PasswordResetToken.used == False)
    pr = db.scalar(stmt)
    if not pr:
        return False
    pr.used = True
    user = db.get(User, pr.user_id)
    user.password_hash = pwd_context.hash(new_password)
    db.commit()
    return True

def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
    user = db.get(User, user_id)
    if not user or not verify_password(old_password, user.password_hash):
        return False
    user.password_hash = pwd_context.hash(new_password)
    db.commit()
    return True