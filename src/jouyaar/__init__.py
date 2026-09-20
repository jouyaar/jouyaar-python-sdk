"""Jouyaar (جویار) — official Python SDK for the agentic search API.

    from jouyaar import Agent
    client = Agent(api_key="sk_live_…")   # or set JOUYAAR_API_KEY
    res = client.search(category="flight", prompt="پرواز تهران به مشهد فردا صبح")
    for q in res.quotes:
        print(q.provider, q.price_toman)
"""

from ._version import __version__
from .client import Agent, AsyncAgent
from .errors import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    InvalidRequestError,
    JouyaarError,
    QuotaExceededError,
    RateLimitError,
)
from .models import (
    Category,
    FieldInfo,
    ProviderMeta,
    Quote,
    SearchResponse,
    SearchResult,
    Seller,
    Usage,
)

# Backwards-compat aliases for the pre-rename class names (≤ v0.1.2). Not documented; prefer Agent.
Jouyaar = Agent
AsyncJouyaar = AsyncAgent

__all__ = [
    "APIConnectionError",
    "APIStatusError",
    "Agent",
    "AsyncAgent",
    "AuthenticationError",
    "Category",
    "FieldInfo",
    "InvalidRequestError",
    "JouyaarError",
    "ProviderMeta",
    "QuotaExceededError",
    "Quote",
    "RateLimitError",
    "SearchResponse",
    "SearchResult",
    "Seller",
    "Usage",
    "__version__",
]
