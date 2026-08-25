"""Typed response models mirroring the Jooyar API.

Loosely typed on purpose (``extra="allow"``): the API can add fields without breaking older SDK
versions. Category-specific quote payloads (flight/bus/lodging/…) are kept as plain dicts so the SDK
doesn't have to track every vertical's schema.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow")


class FieldInfo(_Base):
    name: str
    fa_label: str = ""
    required: bool = False
    choices: Optional[list[str]] = None


class Category(_Base):
    name: str
    fa_title: str = ""
    default_sort: str = "recommended"
    sorts: list[str] = Field(default_factory=list)
    fields: list[FieldInfo] = Field(default_factory=list)


class Seller(_Base):
    provider: str = ""
    deep_link: str = ""
    price_toman: Optional[int] = None


class Quote(_Base):
    provider: str = ""
    plan_name: str = ""
    price_toman: int = 0
    deep_link: str = ""
    coverage: dict = Field(default_factory=dict)
    sellers: list[Seller] = Field(default_factory=list)
    popularity_score: float = 0.0
    provider_rating: float = 0.0
    coverage_score: float = 0.0
    confidence: str = "high"
    # Exactly one vertical payload is set per quote; kept as dicts (see module docstring).
    flight: Optional[dict] = None
    bus: Optional[dict] = None
    train: Optional[dict] = None
    lodging: Optional[dict] = None
    retail: Optional[dict] = None
    internet: Optional[dict] = None
    raw: dict = Field(default_factory=dict)


class ProviderMeta(_Base):
    provider: str
    status: str = "ok"
    count: int = 0
    error: Optional[str] = None


class SearchResponse(_Base):
    quotes: list[Quote] = Field(default_factory=list)
    applied_sort: str = "recommended"
    available_sorts: list[str] = Field(default_factory=list)
    meta: list[ProviderMeta] = Field(default_factory=list)


class SearchResult(_Base):
    """The top-level ``/v1/search`` answer.

    ``ok`` is True when a search ran. When False, ``message`` explains why (blocked, off-topic, or
    missing required fields listed in ``needs``) and ``results`` is None.
    """

    ok: bool
    understood: dict = Field(default_factory=dict)
    sort: str = "recommended"
    message: str = ""
    needs: list[str] = Field(default_factory=list)
    results: Optional[SearchResponse] = None

    @property
    def quotes(self) -> list[Quote]:
        """Convenience: the ranked quotes (empty list if the search returned none)."""
        return self.results.quotes if self.results else []


class Usage(_Base):
    plan: str
    rate_limit_per_min: int
    rate_used_this_minute: int
    monthly_quota: int
    monthly_used: int
    monthly_remaining: int
    monthly_reset: str


# Re-export for `from jouyaar.models import *`
__all__ = [
    "Category",
    "FieldInfo",
    "ProviderMeta",
    "Quote",
    "SearchResponse",
    "SearchResult",
    "Seller",
    "Usage",
]
