from datetime import datetime

from social_insights.analytics import (
    aggregate_insights,
    calculate_engagement_rate,
    hashtag_frequency,
    posting_schedule,
    top_posts,
)
from social_insights.data_models import SocialPost


def make_post(idx: int, day: int, *, likes: int, comments: int, shares: int, content: str = "") -> SocialPost:
    return SocialPost(
        id=str(idx),
        platform="test",
        content=content,
        likes=likes,
        comments=comments,
        shares=shares,
        posted_at=datetime(2023, 1, day, 12, 0),
        raw_payload={},
    )


def test_calculate_engagement_rate_handles_missing_followers():
    post = make_post(1, 1, likes=10, comments=5, shares=5)
    assert calculate_engagement_rate(post) == 20.0
    assert calculate_engagement_rate(post, follower_count=0) == 20.0
    assert calculate_engagement_rate(post, follower_count=100) == 0.2


def test_top_posts_returns_expected_order():
    posts = [
        make_post(1, 1, likes=5, comments=0, shares=0),
        make_post(2, 1, likes=2, comments=0, shares=10),
        make_post(3, 1, likes=10, comments=5, shares=1),
    ]
    top = top_posts(posts, limit=2)
    assert [post.id for post in top] == ["3", "2"]


def test_posting_schedule_returns_weekday_names():
    posts = [
        make_post(1, 1, likes=5, comments=0, shares=0),
        make_post(2, 2, likes=2, comments=0, shares=10),
        make_post(3, 8, likes=10, comments=5, shares=1),
    ]
    schedule = posting_schedule(posts)
    assert set(schedule.keys()) == {"Sunday", "Monday"}


def test_hashtag_frequency_counts_hashtags():
    posts = [
        make_post(1, 1, likes=0, comments=0, shares=0, content="#Fun with #Fun"),
        make_post(2, 1, likes=0, comments=0, shares=0, content="#Data #fun"),
    ]
    frequencies = hashtag_frequency(posts)
    assert frequencies == {"#fun": 3, "#data": 1}


def test_aggregate_insights_combines_metrics():
    posts = [
        make_post(1, 1, likes=5, comments=1, shares=2, content="#one"),
        make_post(2, 2, likes=10, comments=3, shares=4, content="#two"),
    ]
    insights = aggregate_insights(posts, follower_counts={"test": 100})
    assert insights["top_engagement_posts"][0] == "2"
    assert len(insights["engagement_rates"]) == 2
    assert insights["hashtags"] == {"#one": 1, "#two": 1}
