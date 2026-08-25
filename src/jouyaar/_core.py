"""Shared, transport-agnostic helpers for the sync and async clients.

Keeps request construction, error mapping, and retry policy in one place so the two clients only
differ in how they run the HTTP call.
"""

from typing import Any, Optional

import httpx

from ._version import __version__
from .errors import (
    APIStatusError,
    AuthenticationError,
    InvalidRequestError,
    JooyaarError,
    QuotaExceededError,
    RateLimitError,
)

DEFAULT_BASE_URL = "https://api.jouyaar.ir"
USER_AGENT = f"jouyaar-python/{__version__}"


def build_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _error_from_body(status: int, body: Any, headers: httpx.Headers) -> JooyaarError:
    """Map an API error envelope (``{"error": {...}}``) to the right exception class."""
    err = body.get("error", {}) if isinstance(body, dict) else {}
    code = err.get("code")
    message = err.get("message") or err.get("detail") or f"HTTP {status}"
    request_id = err.get("request_id") or headers.get("x-request-id")
    common = {"status_code": status, "code": code, "request_id": request_id}

    if status == 401:
        return AuthenticationError(message, **common)
    if status == 429:
        if code == "quota_exceeded":
            return QuotaExceededError(message, **common)
        ra = headers.get("retry-after")
        retry_after = int(ra) if ra and ra.isdigit() else None
        return RateLimitError(message, retry_after=retry_after, **common)
    if status in (400, 422):
        return InvalidRequestError(message, **common)
    return APIStatusError(message, **common)


def parse_response(resp: httpx.Response) -> Any:
    """Return parsed JSON for a 2xx response, or raise the mapped error."""
    try:
        body = resp.json()
    except Exception:  # non-JSON body (proxy error page, etc.)
        body = None
    if resp.is_success:
        return body
    raise _error_from_body(resp.status_code, body, resp.headers)


def should_retry(status: Optional[int]) -> bool:
    """Retry transient failures: rate limits and 5xx. Never retry 4xx (except 429)."""
    return status is not None and (status == 429 or status >= 500)


def retry_delay(attempt: int, resp: Optional[httpx.Response]) -> float:
    """Backoff seconds for a retry: honor ``Retry-After`` if present, else exponential."""
    if resp is not None:
        ra = resp.headers.get("retry-after")
        if ra and ra.isdigit():
            return float(int(ra))
    return min(2.0**attempt, 10.0)  # 1, 2, 4, … capped at 10s


def build_search_body(
    category: str, prompt: Optional[str], params: Optional[dict], sort: Optional[str]
) -> dict:
    if (prompt is None) == (params is None):
        raise ValueError("Provide exactly one of `prompt` or `params`.")
    body: dict = {"category": category}
    if prompt is not None:
        body["prompt"] = prompt
    if params is not None:
        body["params"] = params
    if sort is not None:
        body["sort"] = sort
    return body
