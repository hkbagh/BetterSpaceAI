"""Analytical helpers for extracting insights from social media posts."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, Iterable, List, Tuple

from .data_models import SocialPost


def calculate_engagement_rate(post: SocialPost, *, follower_count: int | None = None) -> float:
    """Compute engagement rate for a single post.

    If ``follower_count`` is not provided, the raw engagement count is returned.
    """

    if follower_count in (None, 0):
        return float(post.engagement_total)
    return post.engagement_total / float(follower_count)


def top_posts(posts: Iterable[SocialPost], *, metric: str = "engagement", limit: int = 5) -> List[SocialPost]:
    """Return the top performing posts by engagement, likes or comments."""

    key_map = {
        "engagement": lambda p: p.engagement_total,
        "likes": lambda p: p.likes,
        "comments": lambda p: p.comments,
        "shares": lambda p: p.shares,
    }
    metric_key = key_map.get(metric)
    if metric_key is None:
        raise ValueError(f"Unsupported metric '{metric}'")

    sorted_posts = sorted(posts, key=metric_key, reverse=True)
    return sorted_posts[:limit]


def posting_schedule(posts: Iterable[SocialPost]) -> Dict[str, float]:
    """Return the average engagement by weekday."""

    weekday_metrics: Dict[int, List[int]] = defaultdict(list)
    for post in posts:
        weekday_metrics[post.posted_at.weekday()].append(post.engagement_total)

    schedule: Dict[str, float] = {}
    base = datetime(2020, 1, 6)
    for weekday, engagements in weekday_metrics.items():
        average_engagement = mean(engagements)
        schedule[(base + timedelta(days=weekday)).strftime("%A")] = average_engagement
    return schedule


def hashtag_frequency(posts: Iterable[SocialPost]) -> Dict[str, int]:
    """Count hashtag occurrences across post content."""

    counter: Counter[str] = Counter()
    for post in posts:
        for word in post.content.split():
            if word.startswith("#") and len(word) > 1:
                counter[word.lower()] += 1
    return dict(counter)


def aggregate_insights(posts: Iterable[SocialPost], *, follower_counts: Dict[str, int] | None = None) -> Dict[str, Any]:
    """Summarise multiple insights into a single dictionary."""

    posts_list = list(posts)
    follower_counts = follower_counts or {}

    engagement_rates: List[Tuple[str, float]] = []
    for post in posts_list:
        rate = calculate_engagement_rate(post, follower_count=follower_counts.get(post.platform))
        engagement_rates.append((post.id, rate))

    return {
        "top_engagement_posts": [post.id for post in top_posts(posts_list, metric="engagement")],
        "engagement_rates": engagement_rates,
        "schedule": posting_schedule(posts_list),
        "hashtags": hashtag_frequency(posts_list),
    }
