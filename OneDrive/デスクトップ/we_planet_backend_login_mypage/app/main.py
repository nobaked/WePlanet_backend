from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
import traceback

from app.core.database import engine, get_db
from app.models import user as models
from app.models.eco_mission import EcoMission
from app.models.user_activity import UserActivity
from app.core import security
from app.core.oauth import oauth  # Google OAuth
from app.core.config import settings  # ← ここで settings を使う
from app.schemas.user import UserLogin  # ✅ 追加

# Base は models 側で import
from app.models.user import Base
from app.models.eco_badge import EcoBadge

# ✅ 各 API ルーターを import
from app.routers import users, ecoboard, mission, badge

# DB のテーブル作成
models.Base.metadata.create_all(bind=engine)

# FastAPI アプリ
app = FastAPI(title="FastAPI", version="0.1.0")

# ==============================
# Session Middleware
# ==============================
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
)

# ==============================
# CORS Middleware
# ==============================
origins = [o.strip() for o in settings.API_CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# OpenAPI カスタマイズ
# ==============================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        description="API with JWT authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "security" not in method:
                method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ==============================
# ルーター登録
# ==============================
app.include_router(users.router, tags=["users"])
app.include_router(ecoboard.router, prefix="/ecoboard", tags=["ecoboard"])
app.include_router(mission.router, prefix="/mission", tags=["mission"])
app.include_router(badge.router, prefix="/badge", tags=["badge"])

# ==============================
# エンドポイント
# ==============================
@app.get("/")
def root():
    return {"message": "Hello FastAPI"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ==============================
# ローカルログイン（修正版）
# ==============================
@app.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not db_user or not security.verify_password(user_in.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = security.create_access_token(data={"sub": str(db_user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def get_me(current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    total_points = (
        db.query(EcoMission.default_point)
        .join(UserActivity, UserActivity.mission_id == EcoMission.mission_id)
        .filter(UserActivity.user_id == current_user.user_id)
        .all()
    )
    points = sum([p[0] for p in total_points]) if total_points else 0

    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "badge_id": current_user.badge_id,
        "points": points,
    }

# ==============================
# Google OAuth ログイン
# ==============================
@app.get("/login/google")
async def login_google(request: Request):
    # .env から読み込んだ redirect_uri を使う
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    print("DEBUG user_info:", user_info)  # ★デバッグ追加
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Google login failed")

    email = user_info["email"]
    db_user = db.query(models.User).filter(models.User.email == email).first()

    if not db_user:
        db_user = models.User(
            email=email,
            auth_provider="google",
            provider_user_id=user_info["sub"],
            nickname=user_info.get("name"),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    # JWT発行
    access_token = security.create_access_token(data={"sub": str(db_user.user_id)})

    # 開発環境は localhost:3000 へリダイレクト
    redirect_url = f"http://localhost:3000/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)

# ==============================
# グローバル例外ハンドラ
# ==============================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    print("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
