from fastapi import APIRouter
from app.api import users, games, analysis, weaknesses, resources

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(games.router)
api_router.include_router(analysis.router)
api_router.include_router(weaknesses.router)
api_router.include_router(resources.router)
