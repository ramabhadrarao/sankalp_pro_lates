from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime

from common.db.mysql import Base

class PlanningSession(Base):
    __tablename__ = "planning_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)