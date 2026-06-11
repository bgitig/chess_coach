from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.orm import User, Game, MoveEvaluation
from app.models.schemas import SyncRequest, SyncResponse, GameResponse, GamesListResponse
from app.services.chess_com import fetch_games
from app.services.job_queue import create_job, enqueue_job
from app.utils.pgn_parser import extract_eco, extract_played_at

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/sync", response_model=SyncResponse)
async def sync_games(body: SyncRequest, db: AsyncSession = Depends(get_db)):
    username = body.username.strip().lower()

    # Get or create user
    stmt = select(User).where(User.chess_com_username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user = User(chess_com_username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Fetch games from Chess.com
    fetch_months = 3 if body.test_mode else body.months
    try:
        games_data = await fetch_games(username, months=fetch_months)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch games from Chess.com: {str(e)}")

    if not games_data:
        raise HTTPException(status_code=404, detail="No games found for this user in the specified period")

    # Test mode: only the single most recent game
    if body.test_mode:
        games_data = [games_data[-1]]

    # Insert new games; collect failed games for retry
    new_game_ids = []
    retry_game_ids = []
    for gd in games_data:
        existing_result = await db.execute(
            select(Game).where(Game.chess_com_id == gd["chess_com_id"])
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            if existing.analysis_status in ("failed", "pending"):
                existing.analysis_status = "pending"
                retry_game_ids.append(existing.id)
            continue

        game = Game(
            user_id=user.id,
            chess_com_id=gd["chess_com_id"],
            pgn=gd["pgn"],
            time_control=gd["time_control"],
            color_played=gd["color_played"],
            result=gd["result"],
            opponent_rating=gd["opponent_rating"],
            played_at=extract_played_at(gd["pgn"]),
            eco_code=extract_eco(gd["pgn"]),
            analysis_status="pending",
        )
        db.add(game)
        await db.flush()
        new_game_ids.append(game.id)

    # Update last_synced_at
    user.last_synced_at = datetime.utcnow()
    await db.commit()

    all_game_ids = new_game_ids + retry_game_ids
    if not all_game_ids:
        return SyncResponse(
            job_id="",
            games_queued=0,
            message="No new games to analyze. All games already synced.",
        )

    # Create and enqueue analysis job
    job_id = create_job(all_game_ids)
    await enqueue_job(job_id)

    parts = []
    if new_game_ids:
        parts.append(f"{len(new_game_ids)} new")
    if retry_game_ids:
        parts.append(f"{len(retry_game_ids)} retried")
    return SyncResponse(
        job_id=job_id,
        games_queued=len(all_game_ids),
        message=f"Queued {' + '.join(parts)} games for analysis.",
    )


@router.get("", response_model=GamesListResponse)
async def list_games(
    username: str = Query(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    username = username.strip().lower()
    stmt = select(User).where(User.chess_com_username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    count_stmt = select(func.count(Game.id)).where(Game.user_id == user.id)
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * per_page
    games_stmt = (
        select(Game)
        .where(Game.user_id == user.id)
        .order_by(Game.played_at.desc().nullslast())
        .limit(per_page)
        .offset(offset)
    )
    games = (await db.execute(games_stmt)).scalars().all()

    # Attach blunder/mistake counts
    game_responses = []
    for g in games:
        blunder_count = 0
        mistake_count = 0
        if g.analysis_status == "done":
            counts = await db.execute(
                select(MoveEvaluation.error_type, func.count(MoveEvaluation.id))
                .where(MoveEvaluation.game_id == g.id)
                .group_by(MoveEvaluation.error_type)
            )
            for error_type, count in counts.all():
                if error_type == "blunder":
                    blunder_count = count
                elif error_type == "mistake":
                    mistake_count = count

        game_responses.append(GameResponse(
            id=g.id,
            chess_com_id=g.chess_com_id,
            time_control=g.time_control,
            color_played=g.color_played,
            result=g.result,
            opponent_rating=g.opponent_rating,
            played_at=g.played_at,
            analysis_status=g.analysis_status,
            eco_code=g.eco_code,
            blunder_count=blunder_count,
            mistake_count=mistake_count,
        ))

    return GamesListResponse(
        games=game_responses,
        total=total,
        page=page,
        per_page=per_page,
    )
