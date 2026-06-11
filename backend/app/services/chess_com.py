from datetime import datetime, timedelta
import httpx
import re


CHESS_COM_BASE = "https://api.chess.com/pub/player"
HEADERS = {"User-Agent": "ChessTutorApp/1.0 (contact: chess-tutor@example.com)"}


def _get_months(lookback: int) -> list[tuple[int, int]]:
    """Return list of (year, month) tuples for the last N months."""
    months = []
    now = datetime.utcnow()
    for i in range(lookback):
        dt = now - timedelta(days=30 * i)
        months.append((dt.year, dt.month))
    return months


def _parse_color_and_result(game_data: dict, username: str) -> tuple[str | None, str | None, int | None]:
    """Extract color_played, result, opponent_rating from Chess.com game dict."""
    username_lower = username.lower()
    white = game_data.get("white", {})
    black = game_data.get("black", {})

    if white.get("username", "").lower() == username_lower:
        color = "white"
        result_raw = white.get("result", "")
        opponent_rating = black.get("rating")
    elif black.get("username", "").lower() == username_lower:
        color = "black"
        result_raw = black.get("result", "")
        opponent_rating = white.get("rating")
    else:
        return None, None, None

    if result_raw == "win":
        result = "win"
    elif result_raw in ("checkmated", "timeout", "resigned", "lose", "abandoned"):
        result = "loss"
    else:
        result = "draw"

    return color, result, opponent_rating


async def fetch_games(username: str, months: int = 3) -> list[dict]:
    """
    Fetch games from Chess.com for the last N months.
    Returns list of dicts with: chess_com_id, pgn, time_control, color_played,
    result, opponent_rating.
    """
    results = []
    seen_ids = set()

    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
        for year, month in _get_months(months):
            url = f"{CHESS_COM_BASE}/{username}/games/{year}/{month:02d}"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    continue
                raise
            except httpx.RequestError:
                continue

            data = resp.json()
            games = data.get("games", [])

            for game in games:
                game_id = game.get("uuid") or game.get("url", "").split("/")[-1]
                if not game_id or game_id in seen_ids:
                    continue
                seen_ids.add(game_id)

                pgn = game.get("pgn", "")
                if not pgn:
                    continue

                color, result, opp_rating = _parse_color_and_result(game, username)
                time_control = game.get("time_control")

                results.append({
                    "chess_com_id": game_id,
                    "pgn": pgn,
                    "time_control": time_control,
                    "color_played": color,
                    "result": result,
                    "opponent_rating": opp_rating,
                })

    return results
