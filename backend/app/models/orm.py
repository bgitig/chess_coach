from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chess_com_username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    games: Mapped[list["Game"]] = relationship("Game", back_populates="user")
    weakness_scores: Mapped[list["WeaknessScore"]] = relationship("WeaknessScore", back_populates="user")
    resource_progress: Mapped[list["ResourceProgress"]] = relationship("ResourceProgress", back_populates="user")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    chess_com_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    pgn: Mapped[str] = mapped_column(Text)
    time_control: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color_played: Mapped[str | None] = mapped_column(String(10), nullable=True)  # white/black
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)  # win/loss/draw
    opponent_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    played_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    analysis_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/running/done/failed
    eco_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="games")
    move_evaluations: Mapped[list["MoveEvaluation"]] = relationship("MoveEvaluation", back_populates="game")


class MoveEvaluation(Base):
    __tablename__ = "move_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), index=True)
    move_number: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String(10))  # white/black
    fen_before: Mapped[str] = mapped_column(String(200))
    move_uci: Mapped[str] = mapped_column(String(10))
    cp_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    cp_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    cp_loss: Mapped[float] = mapped_column(Float, default=0.0)
    phase: Mapped[str] = mapped_column(String(20))  # opening/middlegame/endgame
    error_type: Mapped[str] = mapped_column(String(20))  # blunder/mistake/inaccuracy/good/best

    game: Mapped["Game"] = relationship("Game", back_populates="move_evaluations")


class WeaknessScore(Base):
    __tablename__ = "weakness_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(50))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    blunder_count: Mapped[int] = mapped_column(Integer, default=0)
    mistake_count: Mapped[int] = mapped_column(Integer, default=0)
    inaccuracy_count: Mapped[int] = mapped_column(Integer, default=0)
    game_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="weakness_scores")

    __table_args__ = (UniqueConstraint("user_id", "category"),)


class ResourceProgress(Base):
    __tablename__ = "resource_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    resource_id: Mapped[str] = mapped_column(String(50))
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="resource_progress")

    __table_args__ = (UniqueConstraint("user_id", "resource_id"),)
