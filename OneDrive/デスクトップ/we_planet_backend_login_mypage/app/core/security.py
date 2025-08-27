from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app import models

# --- パスワードハッシュ用設定 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """平文パスワードをハッシュ化"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文パスワードとハッシュを照合"""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT 関連設定 ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT アクセストークン生成"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """JWT アクセストークンをデコード"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        print(f"[DEBUG] JWT decode error: {e}")
        return None


# --- ユーザー認証関連 ---
def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """メールアドレスとパスワードでユーザー認証"""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# --- JWT Bearer 用 ---
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """JWT から現在のユーザーを取得"""
    token = credentials.credentials
    print("=== [DEBUG] get_current_user called ===")
    print(f"[DEBUG] Token received: {token}")

    payload = decode_access_token(token)
    print(f"[DEBUG] Decoded payload: {payload}")

    if payload is None:
        print("[DEBUG] payload is None → Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    print(f"[DEBUG] User ID from token (sub): {user_id}")

    if user_id is None:
        print("[DEBUG] sub missing in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: no sub",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        print(f"[DEBUG] sub is not an int: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: sub not int",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(models.User.user_id == user_id_int).first()
    print(f"[DEBUG] User fetched from DB: {user}")

    if user is None:
        print(f"[DEBUG] No user found in DB with user_id={user_id_int}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"[DEBUG] Authenticated user: id={user.user_id}, email={user.email}")
    return user
