"""Unit tests for the Jouyaar SDK — HTTP is mocked with respx (no live API)."""

import httpx
import pytest
import respx

import jouyaar
from jouyaar import (
    AsyncJouyaar,
    AuthenticationError,
    InvalidRequestError,
    Jouyaar,
    QuotaExceededError,
    RateLimitError,
)

BASE = "https://api.test"
KEY = "sk_test_abc123"

_SEARCH_OK = {
    "ok": True,
    "understood": {"origin": "THR", "destination": "MHD"},
    "sort": "price",
    "message": "درخواست شما پردازش شد.",
    "needs": [],
    "results": {
        "quotes": [
            {"provider": "علی‌بابا", "plan_name": "W5 1234", "price_toman": 2_500_000,
             "deep_link": "https://alibaba.ir/x", "flight": {"airline": "وارش"}}
        ],
        "applied_sort": "price",
        "available_sorts": ["price", "recommended"],
        "meta": [{"provider": "علی‌بابا", "status": "ok", "count": 1}],
    },
}


def _client() -> Jouyaar:
    return Jouyaar(api_key=KEY, base_url=BASE, max_retries=2)


@respx.mock
def test_search_params_mode_and_auth_header():
    route = respx.post(f"{BASE}/v1/search").mock(return_value=httpx.Response(200, json=_SEARCH_OK))
    with _client() as c:
        res = c.search(category="flight", params={"origin": "THR", "destination": "MHD"})
    assert res.ok is True
    assert res.quotes[0].provider == "علی‌بابا"
    assert res.quotes[0].price_toman == 2_500_000
    assert res.quotes[0].flight["airline"] == "وارش"  # loose vertical payload preserved
    sent = route.calls.last.request
    assert sent.headers["authorization"] == f"Bearer {KEY}"
    assert "jouyaar-python/" in sent.headers["user-agent"]


def test_search_requires_exactly_one_input():
    with _client() as c:
        with pytest.raises(ValueError):
            c.search(category="flight")  # neither
        with pytest.raises(ValueError):
            c.search(category="flight", prompt="x", params={})  # both


@respx.mock
def test_401_raises_authentication_error():
    respx.get(f"{BASE}/v1/usage").mock(
        return_value=httpx.Response(401, json={"error": {"code": "invalid_api_key",
                                                          "message": "bad key", "status": 401,
                                                          "request_id": "req_1"}})
    )
    with _client() as c, pytest.raises(AuthenticationError) as ei:
        c.usage()
    assert ei.value.code == "invalid_api_key"
    assert ei.value.request_id == "req_1"


@respx.mock
def test_429_rate_limit_vs_quota():
    # max_retries=0 so the test doesn't actually sleep the Retry-After.
    respx.get(f"{BASE}/v1/usage").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "42"},
                                    json={"error": {"code": "rate_limit_exceeded", "message": "slow down"}})
    )
    with Jouyaar(api_key=KEY, base_url=BASE, max_retries=0) as c, pytest.raises(RateLimitError) as ei:
        c.usage()
    assert ei.value.retry_after == 42

    respx.get(f"{BASE}/v1/usage").mock(
        return_value=httpx.Response(429, json={"error": {"code": "quota_exceeded", "message": "done"}})
    )
    with Jouyaar(api_key=KEY, base_url=BASE, max_retries=0) as c, pytest.raises(QuotaExceededError):
        c.usage()


@respx.mock
def test_400_raises_invalid_request():
    respx.post(f"{BASE}/v1/search").mock(
        return_value=httpx.Response(400, json={"error": {"code": "invalid_request", "message": "no such category"}})
    )
    with _client() as c, pytest.raises(InvalidRequestError):
        c.search(category="teleport", params={})


@respx.mock
def test_retries_on_500_then_succeeds():
    route = respx.get(f"{BASE}/v1/usage").mock(
        side_effect=[httpx.Response(500), httpx.Response(200, json={
            "plan": "free", "rate_limit_per_min": 30, "rate_used_this_minute": 1,
            "monthly_quota": 1000, "monthly_used": 0, "monthly_remaining": 1000,
            "monthly_reset": "2026-09-01T00:00:00+00:00"})]
    )
    # retry_delay would sleep on 500; patch it to no-op via max backoff of 0 by monkeypatching time.
    import jouyaar._core as core
    orig = core.retry_delay
    core.retry_delay = lambda *a, **k: 0.0
    try:
        with _client() as c:
            u = c.usage()
    finally:
        core.retry_delay = orig
    assert u.plan == "free"
    assert route.call_count == 2


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("JOUYAAR_API_KEY", raising=False)
    with pytest.raises(ValueError):
        Jouyaar(api_key=None, base_url=BASE)


@respx.mock
async def test_async_client():
    respx.get(f"{BASE}/v1/categories").mock(
        return_value=httpx.Response(200, json=[{"name": "flight", "fa_title": "پرواز",
                                                "default_sort": "price", "sorts": ["price"],
                                                "fields": [{"name": "origin", "fa_label": "مبدأ", "required": True}]}])
    )
    async with AsyncJouyaar(api_key=KEY, base_url=BASE) as c:
        cats = await c.categories()
    assert cats[0].name == "flight"
    assert cats[0].fields[0].required is True


def test_version_exported():
    assert jouyaar.__version__
