from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app import models
from app.schemas import user as schemas
from app.core import security

router = APIRouter(prefix="/users", tags=["users"])

# ==============================
# 新規登録
# ==============================
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """ローカルアカウント登録"""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = security.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        password_hash=hashed_pw,
        nickname=user.nickname,
        auth_provider="local",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ==============================
# ログイン
# ==============================
@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """ローカルアカウントログイン"""
    db_user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not db_user or not security.verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = security.create_access_token(data={"sub": str(db_user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}


# ==============================
# Google/既存ユーザー作成 or 取得
# ==============================
@router.post("/")
def create_or_get_user(
    email: str,
    name: str = None,
    provider: str = "google",
    provider_id: str = None,
    db: Session = Depends(get_db)
):
    """Googleログイン時にユーザーを作成または再アクティベート"""
    user = db.query(models.User).filter(models.User.email == email).first()

    if user:
        if user.deleted_at is not None:
            # ✅ 再登録
            user.deleted_at = None
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return {"message": "User re-activated", "user_id": user.user_id}
        return {"message": "User already exists", "user_id": user.user_id}

    new_user = models.User(
        email=email,
        nickname=name,
        auth_provider=provider,
        provider_user_id=provider_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "user_id": new_user.user_id}


# ==============================
# 退会処理
# ==============================
@router.delete("/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """退会処理: deleted_at に現在時刻を入れる"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="User already deleted")

    user.deleted_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "User deleted", "user_id": user.user_id}
