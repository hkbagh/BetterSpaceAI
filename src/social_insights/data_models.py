"""Data models for social media insights."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, MutableMapping, Optional


@dataclass(slots=True)
class SocialPost:
    """Structured representation of a social media post."""

    id: str
    platform: str
    author: str
    text: str
    like_count: int
    share_count: int
    comment_count: int
    posted_at: datetime
    metadata: MutableMapping[str, str]

    @property
    def engagement(self) -> int:
        """Total engagement interactions."""

        return self.like_count + self.share_count + self.comment_count

    @classmethod
    def from_api_payload(
        cls,
        payload: Mapping[str, object],
        platform: str,
        *,
        timestamp_key: str = "created_at",
        text_key: str = "text",
    ) -> "SocialPost":
        """Create a post from an API payload with loose schema.

        Parameters
        ----------
        payload:
            The raw payload coming from the API response.
        platform:
            Social network identifier.
        timestamp_key:
            Name of the field containing an ISO timestamp.
        text_key:
            Name of the field containing the post body.
        """

        try:
            posted_at_value = payload[timestamp_key]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise KeyError(
                f"Missing '{timestamp_key}' in API payload for platform {platform!r}."
            ) from exc

        posted_at = (
            datetime.fromisoformat(posted_at_value.replace("Z", "+00:00"))
            if isinstance(posted_at_value, str)
            else datetime.fromtimestamp(float(posted_at_value))
        )

        metadata: MutableMapping[str, str] = {
            key: str(value)
            for key, value in payload.items()
            if isinstance(key, str)
            and key not in {"id", text_key, "like_count", "share_count", "comment_count"}
        }

        return cls(
            id=str(payload.get("id", "")),
            platform=platform,
            author=str(payload.get("author", payload.get("username", "unknown"))),
            text=str(payload.get(text_key, "")),
            like_count=int(payload.get("like_count", 0)),
            share_count=int(payload.get("share_count", payload.get("retweet_count", 0))),
            comment_count=int(payload.get("comment_count", payload.get("reply_count", 0))),
            posted_at=posted_at,
            metadata=metadata,
        )

    def to_dict(self) -> Mapping[str, object]:
        """Serialize the post into a plain mapping."""

        return {
            "id": self.id,
            "platform": self.platform,
            "author": self.author,
            "text": self.text,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "comment_count": self.comment_count,
            "posted_at": self.posted_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class Insight:
    """Analytical insight derived from social posts."""

    metric: str
    value: float
    description: Optional[str] = None
