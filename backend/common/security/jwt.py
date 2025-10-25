from datetime import datetime, timedelta, timezone
import jwt
from typing import Dict, Any
from common.config import JWT_SECRET, JWT_EXPIRES_MINUTES

ALGORITHM = "HS256"

def create_access_token(data: Dict[str, Any], expires_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or JWT_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

class TokenError(Exception):
    pass

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        raise TokenError(str(e))