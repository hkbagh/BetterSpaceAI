from datetime import datetime

from social_insights.data_models import SocialPost, posts_from_payload


def test_social_post_from_dict_parses_iso_timestamp():
    payload = {
        "id": "1",
        "content": "Test post",
        "likes": 10,
        "comments": 5,
        "shares": 2,
        "posted_at": "2023-01-01T12:00:00",
    }

    post = SocialPost.from_dict(payload, platform="test")

    assert post.id == "1"
    assert post.platform == "test"
    assert post.posted_at == datetime(2023, 1, 1, 12, 0)
    assert post.engagement_total == 17


def test_posts_from_payload_handles_iterables():
    payloads = [
        {
            "id": "1",
            "content": "#one",
            "likes": 1,
            "comments": 0,
            "shares": 0,
            "posted_at": "2023-01-01T00:00:00",
        },
        {
            "id": "2",
            "content": "#two",
            "likes": 2,
            "comments": 0,
            "shares": 0,
            "posted_at": "2023-01-02T00:00:00",
        },
    ]

    posts = posts_from_payload(payloads, platform="test")

    assert len(posts) == 2
    assert {post.id for post in posts} == {"1", "2"}
