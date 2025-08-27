from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.eco_mission import EcoMission
from app.models.user_activity import UserActivity
from app.core.security import get_current_user

router = APIRouter()

@router.get("/summary/me")
def get_ecoboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    ログインユーザーの今月のCO2削減量を返す
    - base_co2_reduction を合計
    - ミッション実行数も返す
    - スギ換算(1本=24g)を計算
    """
    user_id = current_user.user_id

    # 今月の開始日
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)

    # user_activity × eco_mission JOINで合計値を取得
    result = (
        db.query(
            func.sum(EcoMission.base_co2_reduction).label("total_co2"),
            func.count(UserActivity.id).label("missions_count"),
        )
        .join(EcoMission, EcoMission.mission_id == UserActivity.mission_id)
        .filter(UserActivity.user_id == user_id)
        .filter(UserActivity.completed_at >= month_start)
        .first()
    )

    total_co2 = result.total_co2 or 0
    missions_count = result.missions_count or 0

    # スギ換算: 1本=24g
    sugi_count = total_co2 // 24

    return {
        "month": now.strftime("%Y-%m"),
        "sugi": int(sugi_count),
        "co2_g": int(total_co2),
        "missions_done": int(missions_count),
    }
