from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from common.db.mysql import Base

class ProfileImage(Base):
    __tablename__ = "profile_images"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    type = Column(String(20), nullable=False)  # 'photo' or 'logo'
    path = Column(Text, nullable=False)  # local file path for now
    created_at = Column(DateTime, default=datetime.utcnow)

class ProfileUpdateRequest(Base):
    __tablename__ = "profile_update_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    field_name = Column(String(50), nullable=False)
    new_value = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending|approved|rejected
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    action = Column(String(100), nullable=False)
    meta = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)