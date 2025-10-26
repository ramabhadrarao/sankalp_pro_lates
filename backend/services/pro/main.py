from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from common.db.mysql import get_session, Base, engine
from common.security.jwt import decode_token

from services.auth.models import User
from .models import PlanningSession
from .schemas import (
    HoroscopeResponse,
    PlanningSessionCreateRequest,
    PlanningSessionItem,
    PlanningSessionsResponse,
)

app = FastAPI(title="Pro Service", version="1.0.0")
router = APIRouter(prefix="/api/v1")

Base.metadata.create_all(bind=engine)


def require_auth(authorization: str = Header(None), db: Session = Depends(get_session)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


@app.get("/health")
async def health():
    return {"status": "ok", "service": "pro"}

# 220: Daily horoscope (stub)
@router.get("/pro/horoscope/daily", response_model=HoroscopeResponse)
def daily_horoscope(sign: str, date: str):
    # Stubbed content; real implementation would call an astrology API
    summary = f"A reflective day for {sign}. Focus on clarity and balance."
    return HoroscopeResponse(sign=sign, date=date, summary=summary)

# NEW: Weekly horoscope (stub)
@router.get("/pro/horoscope/weekly", response_model=HoroscopeResponse)
def weekly_horoscope(sign: str, week_start: str):
    summary = f"A productive week ahead for {sign}. Plan and execute wisely."
    return HoroscopeResponse(sign=sign, date=week_start, summary=summary)

# NEW: Monthly horoscope (stub)
@router.get("/pro/horoscope/monthly", response_model=HoroscopeResponse)
def monthly_horoscope(sign: str, month: str):
    summary = f"A month of growth for {sign}. Embrace opportunities and learning."
    return HoroscopeResponse(sign=sign, date=month, summary=summary)

# Planning Sessions CRUD
@router.post("/pro/planning-sessions", response_model=PlanningSessionItem)
def create_session(req: PlanningSessionCreateRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    try:
        dt = datetime.fromisoformat(req.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    row = PlanningSession(user_id=user.id, title=req.title, date=dt, notes=req.notes)
    db.add(row)
    db.commit()
    db.refresh(row)
    return PlanningSessionItem(id=row.id, title=row.title, date=row.date.isoformat(), notes=row.notes)

@router.get("/pro/planning-sessions", response_model=PlanningSessionsResponse)
def list_sessions(user: User = Depends(require_auth), db: Session = Depends(get_session)):
    rows = db.scalars(select(PlanningSession).where(PlanningSession.user_id == user.id)).all()
    items = [PlanningSessionItem(id=r.id, title=r.title, date=r.date.isoformat(), notes=r.notes) for r in rows]
    return PlanningSessionsResponse(sessions=items)

@router.get("/pro/planning-sessions/{session_id}", response_model=PlanningSessionItem)
def get_session(session_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    r = db.get(PlanningSession, session_id)
    if not r or r.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    return PlanningSessionItem(id=r.id, title=r.title, date=r.date.isoformat(), notes=r.notes)

@router.put("/pro/planning-sessions/{session_id}", response_model=PlanningSessionItem)
def update_session(session_id: int, req: PlanningSessionCreateRequest, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    r = db.get(PlanningSession, session_id)
    if not r or r.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    r.title = req.title
    try:
        r.date = datetime.fromisoformat(req.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    r.notes = req.notes
    db.commit()
    return PlanningSessionItem(id=r.id, title=r.title, date=r.date.isoformat(), notes=r.notes)

@router.delete("/pro/planning-sessions/{session_id}")
def delete_session(session_id: int, user: User = Depends(require_auth), db: Session = Depends(get_session)):
    r = db.get(PlanningSession, session_id)
    if not r or r.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"deleted": True}

app.include_router(router)