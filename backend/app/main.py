from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.database import init_db
from app.services.job_queue import start_worker, stop_worker
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await start_worker()
    yield
    await stop_worker()


app = FastAPI(title="Chess Tutor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
