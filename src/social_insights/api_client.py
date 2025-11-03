"""API client for retrieving social media data."""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .data_models import SocialPost


class APIClientError(RuntimeError):
    """Raised when the remote API call fails."""


class SocialMediaAPIClient:
    """Lightweight client for social media analytics APIs."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        sample_data_path: Optional[Path] = None,
    ) -> None:
        self._base_url = base_url or os.getenv("SOCIAL_API_BASE_URL")
        self._sample_data_path = sample_data_path or Path(__file__).parent / "sample_data" / "social_posts.json"

    def fetch_posts(
        self,
        platform: str,
        query: str,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_results: int = 100,
        use_sample_data: bool | None = None,
    ) -> list[SocialPost]:
        raw_payload = (
            self._load_sample_data()
            if use_sample_data or (use_sample_data is None and not self._base_url)
            else self._fetch_from_api(platform, query, start_date, end_date, max_results)
        )

        posts = [SocialPost.from_api_payload(item, platform) for item in raw_payload]
        posts.sort(key=lambda post: post.posted_at)
        return posts

    def _fetch_from_api(
        self,
        platform: str,
        query: str,
        start_date: Optional[date],
        end_date: Optional[date],
        max_results: int,
    ) -> Iterable[Mapping[str, object]]:
        if not self._base_url:
            raise APIClientError(
                "SOCIAL_API_BASE_URL is not configured. Provide a base URL or set"
                " use_sample_data=True when calling fetch_posts()."
            )

        params: MutableMapping[str, str] = {
            "platform": platform,
            "query": query,
            "limit": str(max_results),
        }
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        query_string = urlencode(params)
        url = f"{self._base_url.rstrip('/')}/posts?{query_string}"

        try:
            with urlopen(Request(url, method="GET"), timeout=30) as response:
                payload = json.load(response)
        except HTTPError as exc:
            raise APIClientError(
                f"API request failed with status {exc.code}: {exc.reason}"
            ) from exc
        except URLError as exc:
            raise APIClientError(f"Failed to connect to API: {exc.reason}") from exc
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            raise APIClientError("API response is not valid JSON") from exc

        if not isinstance(payload, Mapping):
            raise APIClientError("API response must be a JSON object containing 'data'.")

        data = payload.get("data", [])
        if not isinstance(data, list):  # pragma: no cover - defensive guard
            raise APIClientError("API response 'data' field must be a list.")
        return data

    def _load_sample_data(self) -> Iterable[Mapping[str, object]]:
        if not self._sample_data_path.exists():
            raise FileNotFoundError(
                "Sample data not found. Ensure sample_data/social_posts.json exists."
            )

        with self._sample_data_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, Mapping):
            data = payload.get("data", [])
        else:
            data = payload

        if not isinstance(data, list):  # pragma: no cover - defensive guard
            raise ValueError("Sample data must be a list or contain a 'data' list.")
        return data
