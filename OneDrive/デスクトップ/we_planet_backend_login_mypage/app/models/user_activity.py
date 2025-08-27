from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # ✅ 外部キー追加
    mission_id = Column(Integer, nullable=True)
    completed_at = Column(DateTime, server_default=func.now())
    badge_id = Column(Integer, ForeignKey("eco_badge.badge_id"), nullable=True)

    user = relationship("User", back_populates="activities")
