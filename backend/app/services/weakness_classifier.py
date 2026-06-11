from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm import MoveEvaluation, Game, WeaknessScore, User


CATEGORIES = ["opening", "tactics", "endgame", "positional", "time_management"]

CATEGORY_LABELS = {
    "opening": "Opening Preparation",
    "tactics": "Tactical Awareness",
    "endgame": "Endgame Technique",
    "positional": "Positional Play",
    "time_management": "Time Management",
}


def _compute_score(blunders: int, mistakes: int, inaccuracies: int, total_moves: int) -> float:
    if total_moves == 0:
        return 0.0
    raw = (blunders * 3 + mistakes * 2 + inaccuracies * 1) / total_moves * 100
    return min(100.0, round(raw, 2))


async def compute_weaknesses(user_id: int, db: AsyncSession) -> list[dict]:
    """
    Aggregate move evaluations for a user into weakness scores.
    Returns list of category dicts with scores.
    """
    # Fetch all move evaluations for user's done games
    stmt = (
        select(MoveEvaluation)
        .join(Game, MoveEvaluation.game_id == Game.id)
        .where(Game.user_id == user_id, Game.analysis_status == "done")
    )
    result = await db.execute(stmt)
    evals = result.scalars().all()

    if not evals:
        return []

    # Fetch all done games for time management analysis
    games_stmt = select(Game).where(
        Game.user_id == user_id,
        Game.analysis_status == "done"
    )
    games_result = await db.execute(games_stmt)
    games = games_result.scalars().all()
    game_count = len(games)

    # --- Opening (phase=opening) ---
    opening_evals = [e for e in evals if e.phase == "opening"]
    opening_blunders = sum(1 for e in opening_evals if e.error_type == "blunder")
    opening_mistakes = sum(1 for e in opening_evals if e.error_type == "mistake")
    opening_inaccuracies = sum(1 for e in opening_evals if e.error_type == "inaccuracy")
    opening_score = _compute_score(opening_blunders, opening_mistakes, opening_inaccuracies, len(opening_evals))

    # --- Tactics (blunders in middlegame) ---
    mid_evals = [e for e in evals if e.phase == "middlegame"]
    tactic_blunders = sum(1 for e in mid_evals if e.error_type == "blunder")
    tactic_mistakes = sum(1 for e in mid_evals if e.error_type == "mistake")
    tactic_inaccuracies = sum(1 for e in mid_evals if e.error_type == "inaccuracy")
    tactics_score = _compute_score(tactic_blunders, tactic_mistakes, tactic_inaccuracies, len(mid_evals))

    # --- Endgame (phase=endgame) ---
    end_evals = [e for e in evals if e.phase == "endgame"]
    endgame_blunders = sum(1 for e in end_evals if e.error_type == "blunder")
    endgame_mistakes = sum(1 for e in end_evals if e.error_type == "mistake")
    endgame_inaccuracies = sum(1 for e in end_evals if e.error_type == "inaccuracy")
    endgame_score = _compute_score(endgame_blunders, endgame_mistakes, endgame_inaccuracies, len(end_evals))

    # --- Positional (mistakes, not blunders, in middlegame) ---
    positional_mistakes_only = sum(1 for e in mid_evals if e.error_type == "mistake")
    positional_inaccuracies = sum(1 for e in mid_evals if e.error_type == "inaccuracy")
    positional_score = _compute_score(0, positional_mistakes_only, positional_inaccuracies, len(mid_evals))

    # --- Time Management (games lost + quality drop heuristic) ---
    # Count games with timeout or abandoned losses
    time_losses = sum(
        1 for g in games
        if g.result == "loss" and g.time_control and _is_blitz_or_bullet(g.time_control)
    )
    time_score = min(100.0, round(time_losses / max(game_count, 1) * 100 * 2, 2))

    categories_data = [
        {
            "category": "opening",
            "score": opening_score,
            "blunder_count": opening_blunders,
            "mistake_count": opening_mistakes,
            "inaccuracy_count": opening_inaccuracies,
            "game_count": game_count,
        },
        {
            "category": "tactics",
            "score": tactics_score,
            "blunder_count": tactic_blunders,
            "mistake_count": tactic_mistakes,
            "inaccuracy_count": tactic_inaccuracies,
            "game_count": game_count,
        },
        {
            "category": "endgame",
            "score": endgame_score,
            "blunder_count": endgame_blunders,
            "mistake_count": endgame_mistakes,
            "inaccuracy_count": endgame_inaccuracies,
            "game_count": game_count,
        },
        {
            "category": "positional",
            "score": positional_score,
            "blunder_count": 0,
            "mistake_count": positional_mistakes_only,
            "inaccuracy_count": positional_inaccuracies,
            "game_count": game_count,
        },
        {
            "category": "time_management",
            "score": time_score,
            "blunder_count": 0,
            "mistake_count": 0,
            "inaccuracy_count": 0,
            "game_count": game_count,
        },
    ]

    # Upsert weakness scores to DB
    now = datetime.utcnow()
    for cat_data in categories_data:
        stmt = select(WeaknessScore).where(
            WeaknessScore.user_id == user_id,
            WeaknessScore.category == cat_data["category"]
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.score = cat_data["score"]
            existing.blunder_count = cat_data["blunder_count"]
            existing.mistake_count = cat_data["mistake_count"]
            existing.inaccuracy_count = cat_data["inaccuracy_count"]
            existing.game_count = cat_data["game_count"]
            existing.updated_at = now
        else:
            db.add(WeaknessScore(
                user_id=user_id,
                updated_at=now,
                **cat_data
            ))
    await db.commit()

    return categories_data


def _is_blitz_or_bullet(time_control: str) -> bool:
    """Returns True if time control is blitz (< 10 min) or bullet."""
    try:
        base = int(time_control.split("+")[0])
        return base < 600
    except (ValueError, IndexError):
        return False
