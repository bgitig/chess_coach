from typing import TypedDict


class Resource(TypedDict):
    id: str
    title: str
    url: str
    type: str  # tool / video / course / book
    description: str


RESOURCES: dict[str, list[Resource]] = {
    "opening": [
        {
            "id": "o1",
            "title": "Lichess Opening Explorer",
            "url": "https://lichess.org/analysis",
            "type": "tool",
            "description": "Explore opening theory interactively on a live board with database stats.",
        },
        {
            "id": "o2",
            "title": "Chess.com Opening Explorer",
            "url": "https://www.chess.com/openings",
            "type": "tool",
            "description": "Browse popular openings with master games and win-rate statistics.",
        },
        {
            "id": "o3",
            "title": "GothamChess – Opening Principles (YouTube)",
            "url": "https://www.youtube.com/watch?v=Ka7OFzPcnas",
            "type": "video",
            "description": "Levy Rozman explains core opening principles for beginners and intermediates.",
        },
        {
            "id": "o4",
            "title": "Lichess Opening Study Courses",
            "url": "https://lichess.org/study/topic/Opening/hot",
            "type": "course",
            "description": "Community-created opening studies covering all major systems.",
        },
        {
            "id": "o5",
            "title": "Chess Fundamentals by Capablanca (free PDF)",
            "url": "https://www.gutenberg.org/ebooks/33870",
            "type": "book",
            "description": "Classic free book covering opening principles by world champion Capablanca.",
        },
    ],
    "tactics": [
        {
            "id": "t1",
            "title": "Chess Tempo Tactics Trainer",
            "url": "https://chesstempo.com/chess-tactics",
            "type": "tool",
            "description": "Rated tactics database with thousands of puzzles and spaced repetition.",
        },
        {
            "id": "t2",
            "title": "Lichess Puzzle Storm",
            "url": "https://lichess.org/storm",
            "type": "tool",
            "description": "Blitz through tactics puzzles in 3 minutes to build pattern recognition speed.",
        },
        {
            "id": "t3",
            "title": "Lichess Puzzles",
            "url": "https://lichess.org/training",
            "type": "tool",
            "description": "Infinite free puzzles with difficulty rating and theme filtering.",
        },
        {
            "id": "t4",
            "title": "Daniel Naroditsky – Tactics Study Plan (YouTube)",
            "url": "https://www.youtube.com/watch?v=mIQh3HpBpAk",
            "type": "video",
            "description": "GM Naroditsky explains how to systematically improve tactical vision.",
        },
        {
            "id": "t5",
            "title": "Chess.com Lessons – Tactics",
            "url": "https://www.chess.com/lessons/tactics",
            "type": "course",
            "description": "Free structured lessons covering pins, forks, skewers, and more.",
        },
    ],
    "endgame": [
        {
            "id": "e1",
            "title": "Lichess Endgame Practice",
            "url": "https://lichess.org/practice",
            "type": "tool",
            "description": "Interactive endgame drills with positions from basic to advanced.",
        },
        {
            "id": "e2",
            "title": "Chess Tempo Endgame Trainer",
            "url": "https://chesstempo.com/endgame-training",
            "type": "tool",
            "description": "Structured endgame problem sets with hint and solution modes.",
        },
        {
            "id": "e3",
            "title": "GothamChess – Essential Endgames (YouTube)",
            "url": "https://www.youtube.com/watch?v=tBekA5MoMXs",
            "type": "video",
            "description": "The most important endgame patterns every player must know.",
        },
        {
            "id": "e4",
            "title": "Lichess Endgame Studies",
            "url": "https://lichess.org/study/topic/Endgames/hot",
            "type": "course",
            "description": "Free studies on king and pawn endings, rook endings, and more.",
        },
        {
            "id": "e5",
            "title": "Basic Chess Endings – Free Chapters",
            "url": "https://www.chess.com/article/view/basic-chess-endings",
            "type": "book",
            "description": "Overview of fundamental endgame principles from Reuben Fine's classic work.",
        },
    ],
    "positional": [
        {
            "id": "p1",
            "title": "Lichess Studies – Positional Play",
            "url": "https://lichess.org/study/topic/Middlegame/hot",
            "type": "course",
            "description": "Community studies on weak squares, pawn structure, and piece activity.",
        },
        {
            "id": "p2",
            "title": "Daniel Naroditsky Speed Run (YouTube)",
            "url": "https://www.youtube.com/playlist?list=PLT1F2nOxLHOcmi_qi1BbY6axf5xLFEcit",
            "type": "video",
            "description": "GM Naroditsky narrates his thinking process, emphasizing positional understanding.",
        },
        {
            "id": "p3",
            "title": "Chess.com Lessons – Strategy",
            "url": "https://www.chess.com/lessons/strategy",
            "type": "course",
            "description": "Free lessons on pawn structure, piece coordination, and long-term planning.",
        },
        {
            "id": "p4",
            "title": "My System Concepts – Free Overview",
            "url": "https://www.chess.com/article/view/nimzowitsch-my-system",
            "type": "book",
            "description": "Summary of Nimzowitsch's positional concepts from the classic book My System.",
        },
    ],
    "time_management": [
        {
            "id": "tm1",
            "title": "Chess.com Clock Management Article",
            "url": "https://www.chess.com/article/view/chess-clock-time-management",
            "type": "course",
            "description": "Practical guide to managing your clock effectively in competitive games.",
        },
        {
            "id": "tm2",
            "title": "Lichess Arena Tournaments",
            "url": "https://lichess.org/tournament",
            "type": "tool",
            "description": "Play free blitz/bullet tournaments to practice making decisions under pressure.",
        },
        {
            "id": "tm3",
            "title": "GothamChess – Time Trouble Tips (YouTube)",
            "url": "https://www.youtube.com/watch?v=XD8Z4pKmFmA",
            "type": "video",
            "description": "Practical advice on avoiding time trouble and playing faster when needed.",
        },
        {
            "id": "tm4",
            "title": "Chess Tempo Blitz Tactics",
            "url": "https://chesstempo.com/chess-tactics?problemSet=blitz",
            "type": "tool",
            "description": "Timed tactics mode that builds the habit of finding moves quickly.",
        },
    ],
}


def get_resources(category: str) -> list[Resource]:
    return RESOURCES.get(category, [])


def get_all_resource_ids() -> set[str]:
    ids = set()
    for resources in RESOURCES.values():
        for r in resources:
            ids.add(r["id"])
    return ids
