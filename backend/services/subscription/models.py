from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timedelta

from common.db.mysql import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    tier = Column(String(50), default="free")
    renewal_enabled = Column(Boolean, default=True)

    trial_started_at = Column(DateTime, nullable=True)
    trial_expires_at = Column(DateTime, nullable=True)

    month_start = Column(DateTime, default=datetime.utcnow)
    reports_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def trial_active(self) -> bool:
        return self.trial_expires_at is not None and datetime.utcnow() < self.trial_expires_at