from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime

from common.db.mysql import Base

class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    enabled = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Translation(Base):
    __tablename__ = "translations"
    id = Column(Integer, primary_key=True)
    key = Column(String(255), index=True, nullable=False)
    language_code = Column(String(10), index=True, nullable=False)
    text = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)