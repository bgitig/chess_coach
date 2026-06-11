import asyncio
import sys
import chess
import chess.engine
import chess.pgn
import io
import logging
from app.config import STOCKFISH_PATH, ANALYSIS_DEPTH
from app.utils.pgn_parser import get_move_phase, classify_error

logger = logging.getLogger(__name__)

# Centipawn cap to handle mate scores
CP_CAP = 1000.0


def _score_to_cp(score: chess.engine.Score, turn: chess.Color) -> float | None:
    """Convert engine score to centipawns from white's perspective, capped."""
    if score is None:
        return None
    if score.is_mate():
        mate = score.mate()
        if mate is None:
            return None
        # Score is always from white's perspective (callers pass info["score"].white())
        return CP_CAP if mate > 0 else -CP_CAP
    cp = score.score()
    if cp is None:
        return None
    return max(-CP_CAP, min(CP_CAP, float(cp)))


def _cp_from_player_perspective(cp_white: float | None, color: chess.Color) -> float | None:
    """Flip centipawn score to player's perspective."""
    if cp_white is None:
        return None
    return cp_white if color == chess.WHITE else -cp_white


async def analyze_game(pgn_str: str, color_played: str | None) -> list[dict]:
    """
    Analyze a game PGN using Stockfish.
    Returns list of move evaluation dicts.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _analyze_sync, pgn_str, color_played)


def _analyze_sync(pgn_str: str, color_played: str | None) -> list[dict]:
    # uvicorn --reload on Windows sets WindowsSelectorEventLoopPolicy, which makes
    # asyncio.new_event_loop() return a SelectorEventLoop. SimpleEngine.popen_uci
    # internally calls asyncio.new_event_loop() and then tries to create a subprocess,
    # which SelectorEventLoop raises NotImplementedError for on Windows.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    game = chess.pgn.read_game(io.StringIO(pgn_str))
    if game is None:
        logger.error("PGN parse returned None — invalid PGN?")
        return []

    player_color = chess.WHITE if color_played == "white" else chess.BLACK
    logger.info(f"Analyzing game as {color_played}, stockfish path: {STOCKFISH_PATH}, depth: {ANALYSIS_DEPTH}")

    evaluations = []
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        logger.info("Stockfish engine opened successfully")
    except Exception as e:
        logger.error(f"Failed to open Stockfish at {STOCKFISH_PATH}: {e!r}", exc_info=True)
        return []

    try:
        board = game.board()
        move_number = 0
        cp_before_white = None

        # Get initial evaluation
        try:
            info = engine.analyse(board, chess.engine.Limit(depth=ANALYSIS_DEPTH))
            cp_before_white = _score_to_cp(info["score"].white(), chess.WHITE)
        except Exception:
            cp_before_white = 0.0

        for node in game.mainline():
            move = node.move
            color = board.turn  # color that's about to move

            # Only track moves for the player we're analyzing
            if color != player_color:
                fen_before = board.fen()
                board.push(move)
                # Update cp_before for next iteration (from white's perspective)
                try:
                    info = engine.analyse(board, chess.engine.Limit(depth=ANALYSIS_DEPTH))
                    cp_before_white = _score_to_cp(info["score"].white(), chess.WHITE)
                except Exception:
                    pass
                if color == chess.WHITE:
                    move_number += 1
                continue

            if color == chess.WHITE:
                move_number += 1

            full_move_number = move_number if color == chess.WHITE else move_number
            fen_before = board.fen()
            cp_before_player = _cp_from_player_perspective(cp_before_white, player_color)

            # Make the move
            board.push(move)

            # Evaluate after move
            try:
                info = engine.analyse(board, chess.engine.Limit(depth=ANALYSIS_DEPTH))
                cp_after_white = _score_to_cp(info["score"].white(), chess.WHITE)
            except Exception:
                cp_after_white = cp_before_white

            cp_after_player = _cp_from_player_perspective(cp_after_white, player_color)

            # Compute cp_loss from player's perspective (positive = bad)
            if cp_before_player is not None and cp_after_player is not None:
                cp_loss = max(0.0, cp_before_player - cp_after_player)
            else:
                cp_loss = 0.0

            phase = get_move_phase(full_move_number)
            error_type = classify_error(cp_loss)

            evaluations.append({
                "move_number": full_move_number,
                "color": "white" if player_color == chess.WHITE else "black",
                "fen_before": fen_before,
                "move_uci": move.uci(),
                "cp_before": cp_before_player,
                "cp_after": cp_after_player,
                "cp_loss": cp_loss,
                "phase": phase,
                "error_type": error_type,
            })

            cp_before_white = cp_after_white

    finally:
        engine.quit()

    logger.info(f"Analysis complete: {len(evaluations)} move evaluations produced")
    return evaluations
