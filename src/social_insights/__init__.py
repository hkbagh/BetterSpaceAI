"""Top level package for social insights analytics."""

from .api_client import APIRequest, SocialAPIClient, SocialAPIError
from .aggregator import SocialMediaAggregator
from .analytics import (
    aggregate_insights,
    calculate_engagement_rate,
    hashtag_frequency,
    top_posts,
    posting_schedule,
)
from .data_models import SocialPost

__all__ = [
    "APIRequest",
    "SocialAPIClient",
    "SocialAPIError",
    "SocialMediaAggregator",
    "aggregate_insights",
    "calculate_engagement_rate",
    "hashtag_frequency",
    "top_posts",
    "posting_schedule",
    "SocialPost",
]
