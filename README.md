# Chess Tutor

A personalized chess improvement app that analyzes your Chess.com games with Stockfish to identify your biggest weaknesses and recommends curated free resources.

## Features

- **Game Sync**: Pulls your last 1–6 months of games directly from Chess.com
- **Stockfish Analysis**: Analyzes every move at depth 20, tracking centipawn loss
- **Weakness Detection**: Identifies your weakest areas across 5 categories:
  - Opening Preparation
  - Tactical Awareness
  - Endgame Technique
  - Positional Play
  - Time Management
- **Curated Resources**: Free videos, tools, courses, and books for each weakness
- **Progress Tracking**: Check off resources as you study them

## Stack

- **Backend**: Python, FastAPI, SQLite (via SQLAlchemy async), python-chess, Stockfish
- **Frontend**: React, Vite, Tailwind CSS, Axios

## Prerequisites

- Python 3.11+
- Node.js 18+
- Stockfish binary (see below)

## Setup

### 1. Stockfish

Download Stockfish from https://stockfishchess.org/download/ and place the binary at:
```
backend/engines/stockfish.exe   (Windows)
backend/engines/stockfish       (Linux/macOS)
```

See `backend/engines/README.md` for detailed instructions.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt

uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:5173

## Usage

1. Open http://localhost:5173
2. Enter your Chess.com username in the Sync panel
3. Select how many months of games to analyze and click **Sync Games**
4. Wait for analysis to complete (progress bar shows status)
5. View your **Dashboard** to see ranked weaknesses
6. Click **Study Now** on any weakness card to see recommended resources
7. Check off resources as you complete them

## Project Structure

```
chess_tutor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings (DB path, Stockfish path, etc.)
│   │   ├── database.py          # Async SQLAlchemy setup
│   │   ├── models/
│   │   │   ├── orm.py           # Database table definitions
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   ├── api/                 # Route handlers
│   │   └── services/            # Business logic
│   ├── engines/                 # Place Stockfish binary here
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/client.js        # API calls
        └── components/          # React components
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/users` | Create or fetch user |
| POST | `/api/games/sync` | Sync games from Chess.com |
| GET | `/api/games?username=X` | List games with analysis status |
| GET | `/api/analysis/status/{job_id}` | Background job progress |
| GET | `/api/weaknesses/{username}` | Weakness scores by category |
| GET | `/api/resources/{category}?username=X` | Resources for a category |
| PATCH | `/api/resources/{id}/complete` | Toggle resource completion |
| GET | `/api/health` | Health check |

## Configuration

Edit `backend/app/config.py` to change:
- `ANALYSIS_DEPTH` — Stockfish depth (default: 20; lower = faster)
- `CHESS_COM_MONTHS_LOOKBACK` — Default months to look back
- `CORS_ORIGINS` — Allowed frontend origins
