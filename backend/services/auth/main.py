from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict

from common.db.mysql import Base, engine, get_session
from common.security.jwt import create_access_token, decode_token, TokenError
from common.i18n import get_locale, t

from .schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from .repository import get_user_by_email, create_user, verify_password

app = FastAPI(title="SalahkaarPro Auth Service")

# Create tables on startup
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(request: Request):
    locale = get_locale(request)
    return {"status": "ok", "message": t(locale, "health_ok", "OK")}

@app.post("/auth/register", response_model=Dict[str, str])
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_session)):
    locale = get_locale(request)
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail=t(locale, "email_exists", "Email exists"))

    user = create_user(
        db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        mobile=payload.mobile,
        organization=payload.organization,
        role=payload.role,
        tier=payload.tier or "Starter",
    )
    return {"message": t(locale, "registration_success", "Registered"), "user_id": str(user.id)}

@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_session)):
    locale = get_locale(request)
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail=t(locale, "invalid_credentials", "Invalid credentials"))

    token = create_access_token({"sub": str(user.id), "email": user.email, "tier": user.tier})
    return TokenResponse(access_token=token)

# Dependency to get current user from token

def get_current_user(request: Request, db: Session = Depends(get_session)) -> UserResponse:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    try:
        data = decode_token(token)
    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, data.get("email"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        mobile=user.mobile,
        organization=user.organization,
        role=user.role,
        tier=user.tier,
        verified=user.verified,
    )

@app.get("/auth/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user