from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
from app.models import TrackedUser, UserStats
from app.schemas import LeaderboardResponse, LeaderboardEntry

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "score",
    db: AsyncSession = Depends(get_db)
):
    # Get all active users
    result = await db.execute(
        select(TrackedUser).where(TrackedUser.is_active)
    )
    users = result.scalars().all()

    entries = []
    for user in users:
        # Get latest stats for each user
        stats_result = await db.execute(
            select(UserStats)
            .where(UserStats.user_id == user.id)
            .order_by(UserStats.fetched_at.desc())
            .limit(1)
        )
        stats = stats_result.scalar_one_or_none()
        if not stats:
            continue

        entries.append(LeaderboardEntry(
            rank=0,  # assigned after sorting
            github_username=user.github_username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            score=stats.score,
            commits_30d=stats.commits_30d,
            prs_merged_30d=stats.prs_merged_30d,
            prs_opened_30d=stats.prs_opened_30d,
            reviews_30d=stats.reviews_30d,
            issues_opened_30d=stats.issues_opened_30d,
            stars_received=stats.stars_received,
        ))

    # Sort by chosen metric
    valid_sorts = ["score", "commits_30d", "prs_merged_30d", "reviews_30d", "stars_received"]
    sort_field = sort_by if sort_by in valid_sorts else "score"
    entries.sort(key=lambda x: getattr(x, sort_field), reverse=True)

    # Assign ranks
    for i, entry in enumerate(entries):
        entry.rank = i + 1

    # Paginate
    paginated = entries[offset: offset + limit]

    return LeaderboardResponse(
        total_users=len(entries),
        last_updated=datetime.utcnow(),
        leaderboard=paginated
    )


@router.get("/user/{username}")
async def get_user_rank(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TrackedUser).where(TrackedUser.github_username == username)
    )
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "User not found"}

    stats_result = await db.execute(
        select(UserStats)
        .where(UserStats.user_id == user.id)
        .order_by(UserStats.fetched_at.desc())
        .limit(1)
    )
    stats = stats_result.scalar_one_or_none()

    return {
        "github_username": user.github_username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "score": stats.score if stats else 0,
        "commits_30d": stats.commits_30d if stats else 0,
        "prs_merged_30d": stats.prs_merged_30d if stats else 0,
        "stars_received": stats.stars_received if stats else 0,
    }