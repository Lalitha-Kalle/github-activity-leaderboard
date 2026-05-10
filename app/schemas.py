from pydantic import BaseModel
from datetime import datetime

class AddUserRequest(BaseModel):
    github_username: str

class UserStatsResponse(BaseModel):
    github_username: str
    display_name: str | None
    avatar_url: str | None
    commits_30d: int
    prs_opened_30d: int
    prs_merged_30d: int
    issues_opened_30d: int
    reviews_30d: int
    stars_received: int
    repos_count: int
    score: float

class LeaderboardEntry(BaseModel):
    rank: int
    github_username: str
    display_name: str | None
    avatar_url: str | None
    score: float
    commits_30d: int
    prs_merged_30d: int
    prs_opened_30d: int
    reviews_30d: int
    issues_opened_30d: int
    stars_received: int

class LeaderboardResponse(BaseModel):
    total_users: int
    last_updated: datetime
    leaderboard: list[LeaderboardEntry]