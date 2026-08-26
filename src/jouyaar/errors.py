"""Typed error hierarchy for the Jouyaar SDK.

Every non-2xx API response is raised as a :class:`JouyaarError` subclass carrying the server's
machine-readable ``code`` and ``request_id`` (quote it to support). Branch on the class:

    try:
        client.search(category="flight", prompt="…")
    except jouyaar.RateLimitError as e:
        time.sleep(e.retry_after or 1)
    except jouyaar.AuthenticationError:
        ...
"""

from typing import Optional


class JouyaarError(Exception):
    """Base class for all SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.request_id = request_id

    def __str__(self) -> str:
        bits = [self.message]
        if self.code:
            bits.append(f"code={self.code}")
        if self.request_id:
            bits.append(f"request_id={self.request_id}")
        return " | ".join(bits)


class APIConnectionError(JouyaarError):
    """The request never reached the API (network error, DNS, timeout)."""


class AuthenticationError(JouyaarError):
    """401 — missing, invalid, revoked, or expired API key."""


class InvalidRequestError(JouyaarError):
    """400/422 — the request was rejected (bad category, malformed body, …)."""


class RateLimitError(JouyaarError):
    """429 — per-minute rate limit exceeded. ``retry_after`` is seconds to wait, if provided."""

    def __init__(self, message: str, *, retry_after: Optional[int] = None, **kw) -> None:
        super().__init__(message, **kw)
        self.retry_after = retry_after


class QuotaExceededError(JouyaarError):
    """429 — monthly quota exhausted. Upgrade the plan or wait for the next month."""


class APIStatusError(JouyaarError):
    """Any other non-2xx (e.g. 5xx) response."""
