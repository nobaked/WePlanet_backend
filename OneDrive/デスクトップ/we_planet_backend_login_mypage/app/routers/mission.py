# app/routers/mission.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.eco_mission import EcoMission
from app.models.user_activity import UserActivity
from app.models.user import User
from app.models.eco_badge import EcoBadge
from app.core.security import get_current_user
from datetime import datetime
import random

router = APIRouter()

@router.get("/today")
def get_today_mission(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    今日のミッションをランダムで1つ返す
    """
    missions = db.query(EcoMission).all()
    if not missions:
        raise HTTPException(status_code=404, detail="No missions found")

    mission = random.choice(missions)

    return {
        "mission_id": mission.mission_id,
        "title": mission.title,
        "description": mission.description,
        "base_co2_reduction": mission.base_co2_reduction,
        "default_point": mission.default_point,
    }

@router.post("/complete/{mission_id}")
def complete_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) ,
):

    """
    ミッション完了を記録し、ポイント・削減量・バッジを返す
    """
    user = current_user

    mission = db.query(EcoMission).filter(EcoMission.mission_id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    # ✅ ユーザーの達成済みミッション数をカウント
    completed_count = db.query(UserActivity).filter(
        UserActivity.user_id == user.user_id
    ).count()

    # eco_badge の最大 badge_id を取得
    max_badge_id = db.query(func.max(EcoBadge.badge_id)).scalar()

    badge = None
    if completed_count == 0:
        # ✅ 1回目の達成時は必ず badge_id=1 を付与
        badge = db.query(EcoBadge).filter(EcoBadge.badge_id == 1).first()
    else:
        # ✅ 2回目以降は達成数+1のバッジを付与
        next_badge_id = completed_count + 1
        if next_badge_id <= max_badge_id:
            badge = db.query(EcoBadge).filter(EcoBadge.badge_id == next_badge_id).first()

    # user_activity に記録
    activity = UserActivity(
        user_id=user.user_id,
        mission_id=mission.mission_id,
        completed_at=datetime.now(),
        badge_id=badge.badge_id if badge else None
    )
    db.add(activity)
    db.commit()

    # ✅ デバッグログ
    print(f"[DEBUG] user_id={user.user_id}, completed_count={completed_count}, badge_id={(badge.badge_id if badge else None)}")

    return {
        "message": "Mission completed",
        "mission_id": mission_id,
        "point": mission.default_point,
        "co2": mission.base_co2_reduction,
        "badge": {
            "id": badge.badge_id if badge else None,
            "name": badge.badge_name if badge else None,
            "image": badge.badge_image if badge else None,
        } if badge else None
    }
