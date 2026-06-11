import re
import chess.pgn
import io
from datetime import datetime


def parse_pgn(pgn_str: str) -> chess.pgn.Game | None:
    try:
        return chess.pgn.read_game(io.StringIO(pgn_str))
    except Exception:
        return None


def extract_eco(pgn_str: str) -> str | None:
    match = re.search(r'\[ECO "([^"]+)"\]', pgn_str)
    return match.group(1) if match else None


def extract_played_at(pgn_str: str) -> datetime | None:
    date_match = re.search(r'\[Date "([^"]+)"\]', pgn_str)
    time_match = re.search(r'\[StartTime "([^"]+)"\]', pgn_str)
    if not date_match:
        return None
    date_str = date_match.group(1).replace(".", "-")
    time_str = time_match.group(1) if time_match else "00:00:00"
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None


def get_move_phase(move_number: int) -> str:
    if move_number <= 15:
        return "opening"
    elif move_number <= 40:
        return "middlegame"
    return "endgame"


def classify_error(cp_loss: float) -> str:
    if cp_loss >= 200:
        return "blunder"
    elif cp_loss >= 100:
        return "mistake"
    elif cp_loss >= 50:
        return "inaccuracy"
    elif cp_loss >= 10:
        return "good"
    return "best"
