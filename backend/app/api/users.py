from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.orm import User
from app.models.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
async def create_or_get_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    username = body.chess_com_username.strip().lower()
    stmt = select(User).where(User.chess_com_username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user

    user = User(chess_com_username=username)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{username}", response_model=UserResponse)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    username = username.strip().lower()
    stmt = select(User).where(User.chess_com_username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
