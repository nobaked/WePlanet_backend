from sqlalchemy import Column, Integer, String
from app.core.database import Base


class EcoBadge(Base):
    __tablename__ = "eco_badge"

    badge_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    badge_name = Column(String(100), nullable=False)        # バッジ名
    description = Column(String(255), nullable=True)        # バッジ説明
    category_name = Column(String(100), nullable=True)      # バッジカテゴリ
    badge_image = Column(String(255), nullable=True)        # バッジ画像URL
