from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.eco_badge import EcoBadge
from app.models.user_activity import UserActivity
from app.core.security import get_current_user

router = APIRouter()

@router.get("/badges")
def get_all_badges(db: Session = Depends(get_db)):
    """
    バッジマスターデータをすべて返す（加工せずそのまま）
    """
    badges = db.query(EcoBadge).order_by(EcoBadge.badge_id).all()
    return [
        {
            "badge_id": b.badge_id,
            "badge_name": b.badge_name,
            "description": b.description,
            "category_name": b.category_name,
            "badge_image": b.badge_image,
            "unlock_order": b.badge_id
        }
        for b in badges
    ]


@router.get("/user-progress/me")
def get_user_progress_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ログインユーザーの進捗状況を返す
    - current_badge_count = UserActivity のレコード数
    - total_points, total_co2_reduction は今回は不要なので 0 固定
    """
    user_id = current_user.user_id

    mission_count = db.query(UserActivity).filter(
        UserActivity.user_id == user_id
    ).count()

    return {
        "current_badge_count": mission_count,
        "total_points": 0,              # 今回は不要 → 常に 0
        "total_co2_reduction": 0,       # 今回は不要 → 常に 0
        "total_missions_completed": mission_count
    }
