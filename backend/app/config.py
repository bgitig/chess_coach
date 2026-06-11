import os
import sys
from pathlib import Path

# Windows dev: __file__ resolution breaks in Git Bash, so hardcode.
# Linux prod (Render): resolve normally.
if sys.platform == "win32":
    BASE_DIR = Path(r"C:\projects\chess_tutor\backend")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = (
    os.environ.get("DATABASE_URL")
    or f"sqlite+aiosqlite:///{BASE_DIR / 'chess_tutor.db'}"
)

# Stockfish: env var (set on Render) → local Windows binary → system PATH
_local_stockfish = BASE_DIR / "engines" / "stockfish.exe"
STOCKFISH_PATH = (
    os.environ.get("STOCKFISH_PATH")
    or (str(_local_stockfish) if _local_stockfish.exists() else "stockfish")
)

# CORS: env var (comma-separated) → dev defaults
_cors_env = os.environ.get("CORS_ORIGINS", "")
CORS_ORIGINS = (
    [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _cors_env
    else [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
)

CHESS_COM_MONTHS_LOOKBACK = 1
ANALYSIS_DEPTH = 5
