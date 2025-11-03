"""Command line interface for generating social media insights."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .aggregator import SocialMediaAggregator
from .analytics import aggregate_insights
from .api_client import APIRequest, SocialAPIClient


def load_requests_from_file(path: Path) -> List[APIRequest]:
    """Load API requests from a JSON configuration file."""

    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    requests: List[APIRequest] = []
    for item in config.get("requests", []):
        requests.append(
            APIRequest(
                platform=item["platform"],
                endpoint=item["endpoint"],
                params=item.get("params"),
                headers=item.get("headers"),
            )
        )
    return requests


def configure_client(base_url: str, token_env: str | None = None) -> SocialAPIClient:
    """Create a client optionally injecting authentication headers from environment variables."""

    client = SocialAPIClient(base_url)
    if token_env:
        token = os.getenv(token_env)
        if token:
            client = client.with_auth(Authorization=f"Bearer {token}")
    return client


def run_pipeline(client: SocialAPIClient, requests: Iterable[APIRequest]) -> Dict[str, Any]:
    aggregator = SocialMediaAggregator(client)
    results = aggregator.fetch_many(list(requests))
    posts = aggregator.as_post_list(results)
    return aggregate_insights(posts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate social media insights from API data")
    parser.add_argument("base_url", help="Base URL for the social media API")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to JSON configuration describing API requests",
    )
    parser.add_argument(
        "--token-env",
        dest="token_env",
        default=None,
        help="Environment variable holding an API token",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save insights as JSON",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = configure_client(args.base_url, args.token_env)
    requests = load_requests_from_file(args.config)
    insights = run_pipeline(client, requests)

    if args.output:
        with args.output.open("w", encoding="utf-8") as handle:
            json.dump(insights, handle, indent=2)
    else:
        print(json.dumps(insights, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution entry point
    raise SystemExit(main())
