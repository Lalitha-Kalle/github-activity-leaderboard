from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import users, leaderboard
from app.scheduler import scheduler, refresh_all_stats
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler on app startup
    scheduler.add_job(
        refresh_all_stats,
        trigger="interval",
        hours=settings.STATS_REFRESH_INTERVAL_HOURS,
        id="refresh_stats",
        replace_existing=True
    )
    scheduler.start()
    print(f"[Scheduler] Started — refreshing every {settings.STATS_REFRESH_INTERVAL_HOURS} hour(s)")
    yield
    # Shutdown scheduler on app stop
    scheduler.shutdown()
    print("[Scheduler] Stopped")


app = FastAPI(
    title="GitHub Activity Leaderboard API",
    description="Track and rank GitHub activity for developers",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(leaderboard.router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "message": "GitHub Leaderboard API is running",
        "scheduler": "running" if scheduler.running else "stopped"
    }


@app.post("/api/admin/refresh")
async def manual_refresh():
    """Manually trigger a stats refresh outside the schedule."""
    await refresh_all_stats()
    return {"message": "Stats refreshed successfully"}