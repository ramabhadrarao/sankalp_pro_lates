from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from passlib.context import CryptContext
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)

def create_user(db: Session, **data) -> User:
    password_hash = pwd_context.hash(data.pop("password"))
    user = User(
        password_hash=password_hash,
        locked_fields_after=datetime.utcnow() + timedelta(hours=72),
        **data,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)