from typing import Any, Dict, Optional

from social_insights.api_client import APIRequest, SocialAPIClient
from social_insights.aggregator import SocialMediaAggregator


class FakeResponse:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[Dict[str, Any]] = []

    def get(self, url: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: Optional[float] = None) -> FakeResponse:
        self.calls.append({
            "url": url,
            "params": params,
            "headers": headers,
            "timeout": timeout,
        })
        sample_payload = [
            {
                "id": "1",
                "content": "Example",
                "likes": 1,
                "comments": 1,
                "shares": 1,
                "posted_at": "2023-01-01T00:00:00",
            }
        ]
        return FakeResponse(sample_payload)


def test_aggregator_fetches_and_normalises():
    session = FakeSession()
    client = SocialAPIClient("https://example.com", session=session)
    aggregator = SocialMediaAggregator(client)

    request = APIRequest(platform="test", endpoint="/posts")
    result = aggregator.fetch(request)

    assert result.platform == "test"
    assert len(result.posts) == 1
    assert result.posts[0].engagement_total == 3
    assert session.calls[0]["url"].endswith("/posts")
