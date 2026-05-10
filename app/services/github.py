import json
import httpx
from datetime import datetime, timedelta
from config import settings

GITHUB_API = "https://api.github.com"
AUTH_HEADERS = {
    "Authorization": f"token {settings.GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


async def get_user_profile(username: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/users/{username}",
            headers=AUTH_HEADERS
        )
        resp.raise_for_status()
        return resp.json()


async def get_commit_count(username: str, days: int = 30) -> int:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/search/commits",
            headers={**AUTH_HEADERS, "Accept": "application/vnd.github.cloak-preview+json"},
            params={"q": f"author:{username} committer-date:>{since}", "per_page": 1}
        )
        resp.raise_for_status()
        return resp.json().get("total_count", 0)


async def get_pr_counts(username: str, days: int = 30) -> dict:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    async with httpx.AsyncClient() as client:
        # PRs opened
        opened = await client.get(
            f"{GITHUB_API}/search/issues",
            headers=AUTH_HEADERS,
            params={"q": f"author:{username} type:pr created:>{since}", "per_page": 1}
        )
        opened.raise_for_status()

        # PRs merged
        merged = await client.get(
            f"{GITHUB_API}/search/issues",
            headers=AUTH_HEADERS,
            params={"q": f"author:{username} type:pr merged:>{since}", "per_page": 1}
        )
        merged.raise_for_status()

    return {
        "prs_opened": opened.json().get("total_count", 0),
        "prs_merged": merged.json().get("total_count", 0)
    }


async def get_issue_count(username: str, days: int = 30) -> int:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/search/issues",
            headers=AUTH_HEADERS,
            params={"q": f"author:{username} type:issue created:>{since}", "per_page": 1}
        )
        resp.raise_for_status()
        return resp.json().get("total_count", 0)


async def get_stars_and_repos(username: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/users/{username}/repos",
            headers=AUTH_HEADERS,
            params={"per_page": 100, "type": "owner"}
        )
        resp.raise_for_status()
        repos = resp.json()

    stars = sum(r.get("stargazers_count", 0) for r in repos)
    return {
        "stars_received": stars,
        "repos_count": len(repos)
    }


async def fetch_all_stats(username: str) -> dict:
    """Fetch all stats for a user in one call. Used by scheduler + add user."""
    profile = await get_user_profile(username)
    commits = await get_commit_count(username)
    prs = await get_pr_counts(username)
    issues = await get_issue_count(username)
    stars_repos = await get_stars_and_repos(username)

    return {
        "display_name": profile.get("name") or username,
        "avatar_url": profile.get("avatar_url", ""),
        "commits_30d": commits,
        "prs_opened_30d": prs["prs_opened"],
        "prs_merged_30d": prs["prs_merged"],
        "issues_opened_30d": issues,
        "reviews_30d": 0,        # GitHub API needs special scope for reviews
        "stars_received": stars_repos["stars_received"],
        "repos_count": stars_repos["repos_count"]
    }