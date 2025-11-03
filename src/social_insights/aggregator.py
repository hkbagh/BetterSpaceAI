"""Utilities for aggregating data from multiple social platforms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence

from .api_client import APIRequest, SocialAPIClient
from .data_models import SocialPost, posts_from_payload


@dataclass
class AggregatedResult:
    """Container bundling posts and metadata for a platform."""

    platform: str
    posts: List[SocialPost]
    raw_payload: Any


class SocialMediaAggregator:
    """Retrieve and normalize posts from a collection of social media APIs."""

    def __init__(self, client: SocialAPIClient) -> None:
        self.client = client

    def fetch(self, request: APIRequest, *, mapping_overrides: Dict[str, Any] | None = None) -> AggregatedResult:
        """Fetch posts for a single platform request."""

        payload = self.client.fetch_posts(request)
        overrides = mapping_overrides or {}
        posts = posts_from_payload(payload, platform=request.platform, **overrides)
        return AggregatedResult(platform=request.platform, posts=posts, raw_payload=payload)

    def fetch_many(self, requests: Sequence[APIRequest]) -> List[AggregatedResult]:
        """Fetch and normalize posts for all provided API requests."""

        results: List[AggregatedResult] = []
        for request in requests:
            results.append(self.fetch(request))
        return results

    def as_post_list(self, results: Iterable[AggregatedResult]) -> List[SocialPost]:
        """Flatten aggregated results into a single list of posts."""

        posts: List[SocialPost] = []
        for result in results:
            posts.extend(result.posts)
        return posts
