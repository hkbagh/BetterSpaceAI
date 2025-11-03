"""Analytics for deriving insights from social media data."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from statistics import mean
from typing import Dict, Iterable, List, Mapping

from .data_models import Insight, SocialPost
from .sentiment import SentimentAnalyzer


@dataclass
class InsightGenerator:
    """Generate data-driven insights from social media posts."""

    sentiment_analyzer: SentimentAnalyzer

    def engagement_summary(self, posts: Iterable[SocialPost]) -> List[Insight]:
        posts = list(posts)
        if not posts:
            return []

        total_engagement = sum(post.engagement for post in posts)
        avg_engagement = total_engagement / len(posts)
        insights = [
            Insight(
                metric="total_engagement",
                value=total_engagement,
                description="Sum of likes, shares and comments for the selected timeframe.",
            ),
            Insight(
                metric="avg_engagement",
                value=avg_engagement,
                description="Average interactions per post.",
            ),
        ]

        engagement_by_platform: Dict[str, int] = defaultdict(int)
        for post in posts:
            engagement_by_platform[post.platform] += post.engagement

        for platform, engagement in engagement_by_platform.items():
            insights.append(
                Insight(
                    metric=f"engagement_{platform}",
                    value=engagement,
                    description=f"Total engagement observed on {platform}.",
                )
            )
        return insights

    def top_keywords(self, posts: Iterable[SocialPost], *, top_k: int = 10) -> List[Insight]:
        tokens = []
        for post in posts:
            words = [word.lower().strip("#.,!?:;") for word in post.text.split()]
            tokens.extend(word for word in words if len(word) > 3)

        counter = Counter(tokens)
        return [
            Insight(
                metric=f"keyword_{word}",
                value=count,
                description=f"Keyword '{word}' appeared {count} times.",
            )
            for word, count in counter.most_common(top_k)
        ]

    def sentiment_overview(self, posts: Iterable[SocialPost]) -> List[Insight]:
        posts = list(posts)
        if not posts:
            return []

        sentiments = [self.sentiment_analyzer.score(post.text) for post in posts]
        return [
            Insight(metric="sentiment_mean", value=mean(sentiments), description="Average sentiment score."),
            Insight(metric="sentiment_min", value=min(sentiments), description="Lowest sentiment observed."),
            Insight(metric="sentiment_max", value=max(sentiments), description="Highest sentiment observed."),
        ]

    def posting_cadence(self, posts: Iterable[SocialPost]) -> List[Insight]:
        posts = list(posts)
        if not posts:
            return []

        posts_by_day: Dict[date, int] = defaultdict(int)
        for post in posts:
            posts_by_day[post.posted_at.date()] += 1

        daily_counts = list(posts_by_day.values())
        return [
            Insight(metric="posts_total", value=len(posts), description="Total number of posts."),
            Insight(metric="posts_days", value=len(posts_by_day), description="Number of active days."),
            Insight(metric="posts_per_day_mean", value=mean(daily_counts), description="Average posts per active day."),
        ]

    def generate_all(self, posts: Iterable[SocialPost]) -> Mapping[str, List[Insight]]:
        posts = list(posts)
        return {
            "engagement": self.engagement_summary(posts),
            "keywords": self.top_keywords(posts),
            "sentiment": self.sentiment_overview(posts),
            "cadence": self.posting_cadence(posts),
        }
