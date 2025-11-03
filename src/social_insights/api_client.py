"""HTTP client abstractions for retrieving social media data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol

try:  # pragma: no cover - dependency guard
    import requests  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    requests = None  # type: ignore


class SocialAPIError(RuntimeError):
    """Raised when an API response indicates an error."""


@dataclass
class APIRequest:
    """Description of an HTTP request required to fetch posts from a platform."""

    platform: str
    endpoint: str
    params: Optional[Mapping[str, Any]] = None
    headers: Optional[Mapping[str, str]] = None


class HasJSON(Protocol):
    """Minimal protocol for the ``requests`` response object we depend on."""

    def json(self) -> Any:  # pragma: no cover - protocol definition
        ...

    def raise_for_status(self) -> None:  # pragma: no cover - protocol definition
        ...


class SessionLike(Protocol):
    """Subset of :class:`requests.Session` used by :class:`SocialAPIClient`."""

    def get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HasJSON:
        ...


class SocialAPIClient:
    """Simple HTTP client tailored for social media REST APIs."""

    def __init__(self, base_url: str, *, session: Optional[SessionLike] = None, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        if session is None:
            if requests is None:
                raise ModuleNotFoundError(
                    "requests is required unless a custom session is provided"
                )
            self.session = requests.Session()
        else:
            self.session = session
        self.timeout = timeout

    def build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}" if endpoint else self.base_url

    def fetch_posts(self, request: APIRequest) -> Any:
        """Retrieve raw payloads from the remote API."""

        url = self.build_url(request.endpoint)
        response = self.session.get(
            url,
            params=request.params,
            headers=request.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def with_auth(self, headers: Optional[Mapping[str, str]] = None, **tokens: str) -> "SocialAPIClient":
        """Return a new client that injects authentication headers for every request."""

        session = AuthenticatedSession(self.session, headers=headers, tokens=tokens)
        return SocialAPIClient(self.base_url, session=session, timeout=self.timeout)


class AuthenticatedSession:
    """Session wrapper that injects authentication tokens into every request."""

    def __init__(
        self,
        session: SessionLike,
        *,
        headers: Optional[Mapping[str, str]] = None,
        tokens: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._session = session
        self._headers = dict(headers or {})
        self._tokens = dict(tokens or {})

    def _build_headers(self, extra_headers: Optional[Mapping[str, str]]) -> Dict[str, str]:
        merged: Dict[str, str] = {**self._headers}
        if extra_headers:
            merged.update(extra_headers)
        for key, value in self._tokens.items():
            merged.setdefault(key, value)
        return merged

    def get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HasJSON:
        merged_headers = self._build_headers(headers)
        return self._session.get(url, params=params, headers=merged_headers, timeout=timeout)
