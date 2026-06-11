import os
from pathlib import Path

BASE_DIR = Path(r"C:\projects\chess_tutor\backend")

DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'chess_tutor.db'}"

# Stockfish path: check local engines dir first, fall back to PATH
_local_stockfish = BASE_DIR / "engines" / "stockfish.exe"
STOCKFISH_PATH = str(_local_stockfish) if _local_stockfish.exists() else "stockfish"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CHESS_COM_MONTHS_LOOKBACK = 1
ANALYSIS_DEPTH = 5
