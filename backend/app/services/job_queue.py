import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.database import AsyncSessionLocal
from app.models.orm import Game, MoveEvaluation
from app.services.analysis_engine import analyze_game
from sqlalchemy import select

logger = logging.getLogger(__name__)

# In-memory job tracking
_jobs: dict[str, dict] = {}
_queue: asyncio.Queue = asyncio.Queue()
_worker_task: asyncio.Task | None = None


def create_job(game_ids: list[int]) -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "queued",
        "games_total": len(game_ids),
        "games_done": 0,
        "games_failed": 0,
        "game_ids": game_ids,
    }
    return job_id


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


async def enqueue_job(job_id: str):
    await _queue.put(job_id)


async def _process_job(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        return

    job["status"] = "running"
    game_ids = job["game_ids"]

    for game_id in game_ids:
        async with AsyncSessionLocal() as db:
            try:
                # Fetch game
                stmt = select(Game).where(Game.id == game_id)
                result = await db.execute(stmt)
                game = result.scalar_one_or_none()

                if not game:
                    job["games_failed"] += 1
                    continue

                # Mark as running
                game.analysis_status = "running"
                await db.commit()

                # Run analysis
                evaluations = await analyze_game(game.pgn, game.color_played)

                if not evaluations:
                    game.analysis_status = "failed"
                    await db.commit()
                    job["games_failed"] += 1
                    continue

                # Delete old evaluations for this game
                old_evals = await db.execute(
                    select(MoveEvaluation).where(MoveEvaluation.game_id == game_id)
                )
                for ev in old_evals.scalars().all():
                    await db.delete(ev)

                # Store new evaluations
                for ev in evaluations:
                    db.add(MoveEvaluation(
                        game_id=game_id,
                        move_number=ev["move_number"],
                        color=ev["color"],
                        fen_before=ev["fen_before"],
                        move_uci=ev["move_uci"],
                        cp_before=ev["cp_before"],
                        cp_after=ev["cp_after"],
                        cp_loss=ev["cp_loss"],
                        phase=ev["phase"],
                        error_type=ev["error_type"],
                    ))

                game.analysis_status = "done"
                await db.commit()
                job["games_done"] += 1

            except Exception as e:
                logger.error(f"Error analyzing game {game_id}: {e}", exc_info=True)
                try:
                    game.analysis_status = "failed"
                    await db.commit()
                except Exception:
                    pass
                job["games_failed"] += 1

    job["status"] = "complete"


async def _worker():
    logger.info("Analysis worker started")
    while True:
        try:
            job_id = await _queue.get()
            if job_id is None:
                break
            await _process_job(job_id)
            _queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)


async def start_worker():
    global _worker_task
    _worker_task = asyncio.create_task(_worker())


async def stop_worker():
    global _worker_task
    if _worker_task:
        await _queue.put(None)  # sentinel to stop worker
        try:
            await asyncio.wait_for(_worker_task, timeout=5.0)
        except asyncio.TimeoutError:
            _worker_task.cancel()
