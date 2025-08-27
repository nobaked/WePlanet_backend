from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# これが無いと models 側から Base が import できない
Base = declarative_base()

# DB接続URL
DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# エンジン作成
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "ssl": {"ca": settings.DB_SSL_CA}
    },
)

# セッション作成
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# DBセッションを取得する依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 接続テスト用関数
def test_connection():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

def test_connection():
    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT DATABASE();")).scalar()
        print(f"[DB TEST] Connected to database: {db_name}")
        result = conn.execute(text("SHOW COLUMNS FROM users;"))
        for row in result:
            print(f"[DB TEST] Column: {row}")
