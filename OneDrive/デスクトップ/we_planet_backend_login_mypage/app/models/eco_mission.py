from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class EcoMission(Base):
    __tablename__ = "eco_mission"

    mission_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    base_co2_reduction = Column(Float, nullable=True)
    default_point = Column(Integer, nullable=False, default=0)
