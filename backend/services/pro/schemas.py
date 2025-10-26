from typing import List
from pydantic import BaseModel

class HoroscopeResponse(BaseModel):
    sign: str
    date: str
    summary: str

class PlanningSessionCreateRequest(BaseModel):
    title: str
    date: str  # ISO date string
    notes: str | None = None

class PlanningSessionItem(BaseModel):
    id: int
    title: str
    date: str
    notes: str | None = None

class PlanningSessionsResponse(BaseModel):
    sessions: List[PlanningSessionItem]