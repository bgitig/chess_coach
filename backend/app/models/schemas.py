from datetime import datetime
from pydantic import BaseModel


# --- Users ---

class UserCreate(BaseModel):
    chess_com_username: str


class UserResponse(BaseModel):
    id: int
    chess_com_username: str
    created_at: datetime
    last_synced_at: datetime | None

    model_config = {"from_attributes": True}


# --- Games ---

class SyncRequest(BaseModel):
    username: str
    months: int = 3
    test_mode: bool = False  # if True, only sync and analyze the single most recent game


class SyncResponse(BaseModel):
    job_id: str
    games_queued: int
    message: str


class GameResponse(BaseModel):
    id: int
    chess_com_id: str
    time_control: str | None
    color_played: str | None
    result: str | None
    opponent_rating: int | None
    played_at: datetime | None
    analysis_status: str
    eco_code: str | None
    blunder_count: int = 0
    mistake_count: int = 0

    model_config = {"from_attributes": True}


class GamesListResponse(BaseModel):
    games: list[GameResponse]
    total: int
    page: int
    per_page: int


# --- Analysis ---

class AnalysisStatusResponse(BaseModel):
    job_id: str
    status: str  # queued/running/complete
    games_total: int
    games_done: int
    games_failed: int


# --- Weaknesses ---

class WeaknessResponse(BaseModel):
    category: str
    score: float
    blunder_count: int
    mistake_count: int
    inaccuracy_count: int
    game_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class WeaknessesListResponse(BaseModel):
    username: str
    weaknesses: list[WeaknessResponse]


# --- Resources ---

class ResourceItem(BaseModel):
    id: str
    title: str
    url: str
    type: str  # tool/video/course/book
    description: str
    completed: bool = False


class ResourcesResponse(BaseModel):
    category: str
    resources: list[ResourceItem]


class CompleteResourceRequest(BaseModel):
    username: str
