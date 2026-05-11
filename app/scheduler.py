import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import TrackedUser, UserStats
from app.services.github import fetch_all_stats
from app.services.scorer import calculate_score

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def refresh_all_stats():
    """Fetch fresh GitHub stats for all active users and save to DB."""
    logger.info(f"[Scheduler] Starting stats refresh at {datetime.utcnow()}")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TrackedUser).where(TrackedUser.is_active)
        )
        users = result.scalars().all()

        success, failed = 0, 0
        for user in users:
            try:
                stats = await fetch_all_stats(user.github_username)
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
                success += 1
                logger.info(f"[Scheduler] Refreshed {user.github_username} — score: {score}")

            except Exception as e:
                failed += 1
                logger.error(f"[Scheduler] Failed to refresh {user.github_username}: {e}")

        await db.commit()
        logger.info(f"[Scheduler] Done. Success: {success}, Failed: {failed}")