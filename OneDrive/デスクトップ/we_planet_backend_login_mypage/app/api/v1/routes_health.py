from fastapi import APIRouter
from app.core.database import test_connection

router = APIRouter()

@router.get("/health")
def health():
    try:
        test_connection()
        db = "ok"
    except Exception as e:
        db = f"error: {e.__class__.__name__}"
    return {"status": "ok", "db": db}
