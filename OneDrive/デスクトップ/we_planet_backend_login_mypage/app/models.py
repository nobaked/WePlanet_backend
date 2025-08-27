from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"   # ← DBに合わせる

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Googleログインならnull
    auth_provider = Column(String(50), nullable=True)
    provider_user_id = Column(String(255), nullable=True)
    nickname = Column(String(100), nullable=True)
    badge_id = Column(Integer, ForeignKey("badge.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    activities = relationship("UserActivity", back_populates="user")


class EcoMission(Base):
    __tablename__ = "eco_mission"

    mission_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500))
    base_co2_reduction = Column(Integer)
    default_point = Column(Integer, nullable=False)


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ← 修正
    mission_id = Column(Integer, ForeignKey("eco_mission.mission_id"), nullable=False)
    completed_at = Column(DateTime, server_default=func.now())
    badge_id = Column(Integer, ForeignKey("badge.id"), nullable=True)

    user = relationship("User", back_populates="activities")
    mission = relationship("EcoMission")
