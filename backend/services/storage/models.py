from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from datetime import datetime, timedelta

from common.db.mysql import Base

class StorageFile(Base):
    __tablename__ = "storage_files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=True)
    path = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    deleted = Column(Boolean, default=False)