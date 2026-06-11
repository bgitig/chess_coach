from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.orm import User, WeaknessScore
from app.models.schemas import WeaknessesListResponse, WeaknessResponse
from app.services.weakness_classifier import compute_weaknesses, CATEGORY_LABELS

router = APIRouter(prefix="/weaknesses", tags=["weaknesses"])


@router.get("/{username}", response_model=WeaknessesListResponse)
async def get_weaknesses(username: str, db: AsyncSession = Depends(get_db)):
    username = username.strip().lower()
    stmt = select(User).where(User.chess_com_username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Recompute weaknesses from latest data
    await compute_weaknesses(user.id, db)

    # Fetch stored scores
    scores_stmt = (
        select(WeaknessScore)
        .where(WeaknessScore.user_id == user.id)
        .order_by(WeaknessScore.score.desc())
    )
    scores = (await db.execute(scores_stmt)).scalars().all()

    weaknesses = [
        WeaknessResponse(
            category=s.category,
            score=s.score,
            blunder_count=s.blunder_count,
            mistake_count=s.mistake_count,
            inaccuracy_count=s.inaccuracy_count,
            game_count=s.game_count,
            updated_at=s.updated_at,
        )
        for s in scores
    ]

    return WeaknessesListResponse(username=username, weaknesses=weaknesses)
