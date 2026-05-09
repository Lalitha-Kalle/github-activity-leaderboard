import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class TrackedUser(Base):
    __tablename__ = "tracked_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_username: Mapped[str] = mapped_column(String(39), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    stats: Mapped[list["UserStats"]] = relationship("UserStats", back_populates="user")


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracked_users.id"))
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    commits_30d: Mapped[int] = mapped_column(Integer, default=0)
    prs_opened_30d: Mapped[int] = mapped_column(Integer, default=0)
    prs_merged_30d: Mapped[int] = mapped_column(Integer, default=0)
    issues_opened_30d: Mapped[int] = mapped_column(Integer, default=0)
    reviews_30d: Mapped[int] = mapped_column(Integer, default=0)
    stars_received: Mapped[int] = mapped_column(Integer, default=0)
    repos_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["TrackedUser"] = relationship("TrackedUser", back_populates="stats")


class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    rankings: Mapped[dict] = mapped_column(JSON)