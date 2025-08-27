from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ✅ id → user_id
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    auth_provider = Column(String(50), nullable=True)
    provider_user_id = Column(String(255), nullable=True)
    nickname = Column(String(100), nullable=True)
    badge_id = Column(Integer, nullable=True)

    # ✅ 追加: 作成日時・更新日時
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    activities = relationship("UserActivity", back_populates="user")
