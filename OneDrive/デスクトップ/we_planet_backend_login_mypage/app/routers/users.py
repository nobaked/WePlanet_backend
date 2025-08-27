from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app import models
from app.core.security import get_password_hash
from app.schemas.user import GoogleUserCreate, LocalUserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


# -----------------------------
# Googleログイン用: 新規作成 or 既存取得
# -----------------------------
@router.post("", response_model=UserResponse)   # ← /users に対応
@router.post("/", response_model=UserResponse)  # ← /users/ に対応
def create_or_get_user(
    user_in: GoogleUserCreate,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()

    if user:
        # 既存ユーザーがいればそのまま返す
        return {"message": "User already exists", "user_id": user.user_id}

    # 新規作成
    new_user = models.User(
        email=user_in.email,
        nickname=user_in.name,
        auth_provider=user_in.provider,
        provider_user_id=user_in.provider_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created", "user_id": new_user.user_id}


# -----------------------------
# ローカル登録用
# -----------------------------
@router.post("/register", response_model=UserResponse)
def register_local_user(
    user_in: LocalUserCreate,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()

    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    # 新規作成
    new_user = models.User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        nickname=user_in.nickname,
        auth_provider="local",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Local user created", "user_id": new_user.user_id}
