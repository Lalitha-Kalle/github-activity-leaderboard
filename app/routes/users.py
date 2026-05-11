from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import TrackedUser, UserStats
from app.schemas import AddUserRequest
from app.services.github import fetch_all_stats
from app.services.scorer import calculate_score

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/")
async def add_user(payload: AddUserRequest, db: AsyncSession = Depends(get_db)):
    # Check if already tracked
    result = await db.execute(
        select(TrackedUser).where(TrackedUser.github_username == payload.github_username)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User already being tracked")

    # Fetch stats from GitHub
    try:
        stats = await fetch_all_stats(payload.github_username)
    except Exception:
        raise HTTPException(status_code=404, detail=f"GitHub user '{payload.github_username}' not found")

    # Save user
    user = TrackedUser(
        github_username=payload.github_username,
        display_name=stats["display_name"],
        avatar_url=stats["avatar_url"]
    )
    db.add(user)
    await db.flush()  # get user.id before committing

    # Save initial stats
    score = calculate_score(stats)
    user_stats = UserStats(
        user_id=user.id,
        commits_30d=stats["commits_30d"],
        prs_opened_30d=stats["prs_opened_30d"],
        prs_merged_30d=stats["prs_merged_30d"],
        issues_opened_30d=stats["issues_opened_30d"],
        reviews_30d=stats["reviews_30d"],
        stars_received=stats["stars_received"],
        repos_count=stats["repos_count"],
        score=score
    )
    db.add(user_stats)
    await db.commit()

    return {
        "message": "User added successfully",
        "github_username": user.github_username,
        "display_name": user.display_name,
        "score": score
    }


@router.get("/")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TrackedUser).where(TrackedUser.is_active)
    )
    users = result.scalars().all()
    return {"total": len(users), "users": [
        {"github_username": u.github_username, "display_name": u.display_name}
        for u in users
    ]}


@router.delete("/{username}")
async def remove_user(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TrackedUser).where(TrackedUser.github_username == username)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False  # soft delete
    await db.commit()
    return {"message": f"{username} removed from leaderboard"}