import asyncio
import sys
import chess.engine
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import STOCKFISH_PATH
from app.database import get_db
from app.models.orm import Game, User
from app.models.schemas import AnalysisStatusResponse
from app.services.job_queue import create_job, enqueue_job, get_job

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/test-stockfish")
async def test_stockfish():
    def _test():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        try:
            engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            info = engine.analyse(chess.Board(), chess.engine.Limit(depth=1))
            engine.quit()
            return {"ok": True, "score": str(info["score"])}
        except Exception as e:
            return {"ok": False, "error": repr(e), "type": type(e).__name__}
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _test)


@router.get("/debug")
async def debug_analysis(
    username: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Run analysis on the latest game synchronously and return raw results or error details."""
    import traceback
    from app.services.analysis_engine import _analyze_sync

    username = username.strip().lower()
    stmt = select(User).where(User.chess_com_username == username)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    latest_game = (
        await db.execute(
            select(Game)
            .where(Game.user_id == user.id)
            .order_by(Game.played_at.desc().nullslast())
            .limit(1)
        )
    ).scalar_one_or_none()
    if not latest_game:
        raise HTTPException(status_code=404, detail="No games found")

    try:
        loop = asyncio.get_running_loop()
        evals = await loop.run_in_executor(None, _analyze_sync, latest_game.pgn, latest_game.color_played)
        return {
            "ok": True,
            "game_id": latest_game.id,
            "color_played": latest_game.color_played,
            "evaluations_count": len(evals),
            "sample": evals[:5],
        }
    except Exception as e:
        return {
            "ok": False,
            "error": repr(e),
            "traceback": traceback.format_exc(),
        }


@router.post("/run-test")
async def run_test_analysis(
    username: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Queue analysis for the single most recently synced game. Useful for debugging."""
    username = username.strip().lower()
    stmt = select(User).where(User.chess_com_username == username)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    latest_game = (
        await db.execute(
            select(Game)
            .where(Game.user_id == user.id)
            .order_by(Game.played_at.desc().nullslast())
            .limit(1)
        )
    ).scalar_one_or_none()

    if not latest_game:
        raise HTTPException(status_code=404, detail="No games found for this user")

    latest_game.analysis_status = "pending"
    await db.commit()

    job_id = create_job([latest_game.id])
    await enqueue_job(job_id)

    return {
        "job_id": job_id,
        "game_id": latest_game.id,
        "chess_com_id": latest_game.chess_com_id,
        "color_played": latest_game.color_played,
        "message": "Queued latest game for analysis",
    }


@router.get("/status/{job_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return AnalysisStatusResponse(
        job_id=job_id,
        status=job["status"],
        games_total=job["games_total"],
        games_done=job["games_done"],
        games_failed=job["games_failed"],
    )
