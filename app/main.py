from fastapi import FastAPI
from app.routes import users, leaderboard

app = FastAPI(
    title="GitHub Activity Leaderboard API",
    description="Track and rank GitHub activity for developers",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(leaderboard.router)

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "GitHub Leaderboard API is running"}