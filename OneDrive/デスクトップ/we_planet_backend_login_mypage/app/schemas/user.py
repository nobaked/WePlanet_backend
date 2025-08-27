from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# 共通: DBから返す用
class UserBase(BaseModel):
    user_id: int
    email: EmailStr
    nickname: Optional[str] = None
    auth_provider: Optional[str] = None
    provider_user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# -----------------------------
# Googleログイン用スキーマ
# -----------------------------
class GoogleUserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    provider: str = "google"
    provider_id: Optional[str] = None


# -----------------------------
# ローカル登録用スキーマ
# -----------------------------
class LocalUserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: Optional[str] = None


# -----------------------------
# レスポンス用スキーマ
# -----------------------------
class UserResponse(BaseModel):
    message: str
    user_id: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str