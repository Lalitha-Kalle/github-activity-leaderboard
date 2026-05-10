WEIGHTS = {
    "commits_30d":      1.0,
    "prs_merged_30d":   3.0,
    "prs_opened_30d":   1.5,
    "reviews_30d":      2.0,
    "issues_opened_30d": 0.5,
    "stars_received":   0.1,
}

def calculate_score(stats: dict) -> float:
    return round(
        sum(stats.get(metric, 0) * weight
            for metric, weight in WEIGHTS.items()),
        2
    )