"""Simple rule-based sentiment analyzer."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Set

POSITIVE_WORDS: Set[str] = {
    "good",
    "great",
    "love",
    "excellent",
    "positive",
    "awesome",
    "fantastic",
    "happy",
    "success",
}

NEGATIVE_WORDS: Set[str] = {
    "bad",
    "terrible",
    "hate",
    "awful",
    "negative",
    "sad",
    "angry",
    "problem",
    "fail",
}


@dataclass
class SentimentAnalyzer:
    """Naive lexicon-based sentiment scoring."""

    positive_words: Iterable[str] = field(default_factory=lambda: frozenset(POSITIVE_WORDS))
    negative_words: Iterable[str] = field(default_factory=lambda: frozenset(NEGATIVE_WORDS))

    def score(self, text: str) -> float:
        words = [token.strip("#.,!?:;\"'").lower() for token in text.split()]
        positive_hits = sum(1 for word in words if word in self.positive_words)
        negative_hits = sum(1 for word in words if word in self.negative_words)
        total = positive_hits + negative_hits
        if total == 0:
            return 0.0
        return (positive_hits - negative_hits) / total
