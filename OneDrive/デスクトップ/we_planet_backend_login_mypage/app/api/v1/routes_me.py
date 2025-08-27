from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Badge(BaseModel):
    id: str
    name: str

class MeResponse(BaseModel):
    id: str
    email: str
    nickname: str
    points: int
    badges: list[Badge] = []

@router.get("/me", response_model=MeResponse)
def get_me() -> MeResponse:
    # まずはダミー返却（のちほどDBに差し替え）
    return MeResponse(
        id="u_123",
        email="demo@weplanet.example",
        nickname="エコファミリー",
        points=1520,
        badges=[
            Badge(id="b1", name="節電スター"),
            Badge(id="b2", name="節水マスター"),
            Badge(id="b3", name="リサイクル名人"),
        ],
    )
