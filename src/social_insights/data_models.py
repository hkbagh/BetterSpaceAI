"""Data models used across the social insights package."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List


@dataclass
class SocialPost:
    """Representation of a post retrieved from a social media API."""

    id: str
    platform: str
    content: str
    likes: int
    comments: int
    shares: int
    posted_at: datetime
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    @property
    def engagement_total(self) -> int:
        """Return the total engagement for the post."""

        return self.likes + self.comments + self.shares

    @classmethod
    def from_dict(
        cls,
        payload: Dict[str, Any],
        *,
        id_field: str = "id",
        content_field: str = "content",
        like_field: str = "likes",
        comment_field: str = "comments",
        share_field: str = "shares",
        timestamp_field: str = "posted_at",
        timestamp_format: str | None = None,
        platform: str,
    ) -> "SocialPost":
        """Create a :class:`SocialPost` from a payload dictionary.

        Parameters
        ----------
        payload:
            Raw data representing a social media post.
        id_field, content_field, like_field, comment_field, share_field,
        timestamp_field:
            Keys used to map values in ``payload``.
        timestamp_format:
            Optional strptime format when the timestamp is not ISO 8601.
        platform:
            Name of the platform that provided the data.
        """

        posted_raw = payload.get(timestamp_field)
        if posted_raw is None:
            raise ValueError("payload missing timestamp field")

        if isinstance(posted_raw, (int, float)):
            posted_at = datetime.fromtimestamp(float(posted_raw))
        elif isinstance(posted_raw, str):
            if timestamp_format:
                posted_at = datetime.strptime(posted_raw, timestamp_format)
            else:
                posted_at = datetime.fromisoformat(posted_raw)
        elif isinstance(posted_raw, datetime):
            posted_at = posted_raw
        else:
            raise TypeError("unsupported timestamp type")

        def _coerce_int(value: Any) -> int:
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return int(value)
            if isinstance(value, str) and value.isdigit():
                return int(value)
            raise TypeError(f"Cannot convert {value!r} to integer engagement metric")

        likes = _coerce_int(payload.get(like_field, 0))
        comments = _coerce_int(payload.get(comment_field, 0))
        shares = _coerce_int(payload.get(share_field, 0))

        return cls(
            id=str(payload.get(id_field)),
            platform=platform,
            content=str(payload.get(content_field, "")),
            likes=likes,
            comments=comments,
            shares=shares,
            posted_at=posted_at,
            raw_payload=dict(payload),
        )


def posts_from_payload(
    payloads: Iterable[Dict[str, Any]],
    *,
    platform: str,
    **kwargs: Any,
) -> List[SocialPost]:
    """Convert an iterable of dictionaries into :class:`SocialPost` objects."""

    return [SocialPost.from_dict(payload, platform=platform, **kwargs) for payload in payloads]
