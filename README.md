# BetterSpaceAI

This project demonstrates a data-driven approach to extracting social media insights. It bundles:

- A flexible API client capable of calling a live REST endpoint or falling back to bundled sample data.
- Analytics utilities to compute engagement, keyword, sentiment, and posting cadence metrics.
- A command line interface for generating insight reports from social media conversations.

## Getting started

The toolkit only depends on Python's standard library. Run the CLI against the sample dataset with:

```bash
PYTHONPATH=src python -m social_insights.main twitter "workspace" --sample-data
```

To use a live API, set the `SOCIAL_API_BASE_URL` environment variable to a compatible endpoint and omit `--sample-data`.

The generated insights can be printed to the console or written to a JSON file via the `--output` flag.
