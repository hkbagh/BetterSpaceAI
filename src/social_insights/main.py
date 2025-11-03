"""Command line interface for generating social media insights."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .analytics import InsightGenerator
from .api_client import SocialMediaAPIClient
from .sentiment import SentimentAnalyzer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate social media insights")
    parser.add_argument("platform", help="Social media platform identifier")
    parser.add_argument("query", help="Search query or hashtag")
    parser.add_argument("--start", dest="start_date", help="ISO start date (YYYY-MM-DD)")
    parser.add_argument("--end", dest="end_date", help="ISO end date (YYYY-MM-DD)")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of posts to retrieve")
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Use bundled sample dataset instead of live API",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the insights report as JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    start_date = datetime.fromisoformat(args.start_date).date() if args.start_date else None
    end_date = datetime.fromisoformat(args.end_date).date() if args.end_date else None

    client = SocialMediaAPIClient()
    posts = client.fetch_posts(
        args.platform,
        args.query,
        start_date=start_date,
        end_date=end_date,
        max_results=args.max_results,
        use_sample_data=args.sample_data,
    )

    sentiment = SentimentAnalyzer()
    generator = InsightGenerator(sentiment)
    insights = generator.generate_all(posts)

    serializable = {
        category: [
            {
                "metric": insight.metric,
                "value": insight.value,
                "description": insight.description,
            }
            for insight in items
        ]
        for category, items in insights.items()
    }

    if args.output:
        args.output.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    else:
        print(json.dumps(serializable, indent=2))


if __name__ == "__main__":
    main()
