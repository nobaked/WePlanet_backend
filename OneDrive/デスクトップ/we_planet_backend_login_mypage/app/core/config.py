from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # --- Azure MySQL 接続情報 ---
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSL_CA: Optional[str] = None  # ← SSL証明書パス

    # --- CORS設定 ---
    API_CORS_ORIGINS: str = "*"  # デフォルトは全部許可（本番では適切に絞る）

    # --- JWT設定 ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Google OAuth ---
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8001/auth/google/callback"

    # --- セッション管理 ---
    SESSION_SECRET_KEY: str  # ← ここを追加！

    # --- .env 読み込み設定 ---
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    # デバッグ用ログ（PWは長さだけ）
    print(
        f"[Settings Loaded] DB_HOST={s.DB_HOST}, DB_NAME={s.DB_NAME}, "
        f"DB_USER={s.DB_USER}, PW_LEN={len(s.DB_PASSWORD) if s.DB_PASSWORD else 0}, "
        f"DB_SSL_CA={s.DB_SSL_CA}, API_CORS_ORIGINS={s.API_CORS_ORIGINS}, "
        f"JWT_ALGO={s.JWT_ALGORITHM}, JWT_EXPIRE={s.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}, "
        f"GOOGLE_CLIENT_ID={'set' if s.GOOGLE_CLIENT_ID else 'missing'}, "
        f"SESSION_SECRET_KEY_LEN={len(s.SESSION_SECRET_KEY) if s.SESSION_SECRET_KEY else 0}"
    )
    return s

settings = get_settings()
