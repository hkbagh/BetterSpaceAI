# BetterSpaceAI

This repository now includes a data-driven toolkit for producing social media insights from HTTP APIs. The toolkit focuses on keeping the workflow reproducible: you describe the endpoints that should be queried, fetch the data through a lightweight client, and run a collection of analytics helpers that highlight engagement trends.

## Features

- **API abstraction** – `SocialAPIClient` wraps `requests` to make authenticated calls and normalise responses across platforms.
- **Aggregation pipeline** – `SocialMediaAggregator` converts raw API payloads into strongly typed `SocialPost` objects that are ready for analysis.
- **Insight generation** – Helper functions calculate engagement rates, identify top-performing posts, highlight effective posting schedules, and count hashtag usage.
- **Command line interface** – A CLI driver loads API request definitions from JSON, runs the aggregation pipeline, and outputs a consolidated insight report.
- **Test coverage** – Pytest test-suite demonstrating the behaviour of the most critical building blocks.

## Quick start

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Describe the API calls that should be performed in a configuration file:

   ```json
   {
     "requests": [
       {
         "platform": "contoso",
         "endpoint": "/v1/posts",
         "params": {"limit": 50}
       }
     ]
   }
   ```

3. Run the CLI to fetch the data and generate the insights:

   ```bash
   python -m social_insights.cli https://api.contoso.social --config requests.json --token-env CONTOSO_TOKEN
   ```

   The CLI prints a JSON summary by default, or you can save the result with `--output insights.json`.

## Running tests

```bash
pytest
```
