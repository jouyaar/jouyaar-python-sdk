"""Sync (:class:`Jouyaar`) and async (:class:`AsyncJouyaar`) API clients.

    from jouyaar import Jouyaar
    client = Jouyaar()                      # reads JOUYAAR_API_KEY
    res = client.search(category="flight", prompt="پرواز تهران به مشهد فردا صبح")
    for q in res.quotes:
        print(q.provider, q.price_toman)
"""

from __future__ import annotations

import asyncio
import os
import time

import httpx

from . import _core
from .errors import APIConnectionError
from .models import Category, SearchResult, Usage


def _resolve_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("JOUYAAR_API_KEY")
    if not key:
        raise ValueError("An API key is required. Pass api_key=… or set JOUYAAR_API_KEY.")
    return key


def _resolve_base(base_url: str | None) -> str:
    return (base_url or os.environ.get("JOUYAAR_BASE_URL") or _core.DEFAULT_BASE_URL).rstrip("/")


class Jouyaar:
    """Synchronous client. Use as a context manager, or call :meth:`close` when done."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._base_url = _resolve_base(base_url)
        self._max_retries = max_retries
        self._headers = _core.build_headers(_resolve_key(api_key))
        self._client = http_client or httpx.Client(timeout=timeout)
        self._owns_client = http_client is None

    def _request(self, method: str, path: str, *, json: dict | None = None):
        url = self._base_url + path
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._client.request(method, url, headers=self._headers, json=json)
            except httpx.HTTPError as exc:
                if attempt < self._max_retries:
                    time.sleep(_core.retry_delay(attempt, None))
                    continue
                raise APIConnectionError(f"Request to {url} failed: {exc}") from exc
            if _core.should_retry(resp.status_code) and attempt < self._max_retries:
                time.sleep(_core.retry_delay(attempt, resp))
                continue
            return _core.parse_response(resp)
        raise AssertionError("unreachable")  # pragma: no cover

    def search(
        self,
        category: str,
        *,
        prompt: str | None = None,
        params: dict | None = None,
        sort: str | None = None,
    ) -> SearchResult:
        """Search one category. Pass ``params`` (structured, LLM-free) or ``prompt`` (natural
        language) — exactly one."""
        body = _core.build_search_body(category, prompt, params, sort)
        return SearchResult.model_validate(self._request("POST", "/v1/search", json=body))

    def categories(self) -> list[Category]:
        return [Category.model_validate(c) for c in self._request("GET", "/v1/categories")]

    def usage(self) -> Usage:
        return Usage.model_validate(self._request("GET", "/v1/usage"))

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Jouyaar:
        return self

    def __exit__(self, *exc) -> None:
        self.close()


class AsyncJouyaar:
    """Asynchronous client. Use ``async with`` or call :meth:`aclose` when done."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = _resolve_base(base_url)
        self._max_retries = max_retries
        self._headers = _core.build_headers(_resolve_key(api_key))
        self._client = http_client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = http_client is None

    async def _request(self, method: str, path: str, *, json: dict | None = None):
        url = self._base_url + path
        for attempt in range(self._max_retries + 1):
            try:
                resp = await self._client.request(method, url, headers=self._headers, json=json)
            except httpx.HTTPError as exc:
                if attempt < self._max_retries:
                    await asyncio.sleep(_core.retry_delay(attempt, None))
                    continue
                raise APIConnectionError(f"Request to {url} failed: {exc}") from exc
            if _core.should_retry(resp.status_code) and attempt < self._max_retries:
                await asyncio.sleep(_core.retry_delay(attempt, resp))
                continue
            return _core.parse_response(resp)
        raise AssertionError("unreachable")  # pragma: no cover

    async def search(
        self,
        category: str,
        *,
        prompt: str | None = None,
        params: dict | None = None,
        sort: str | None = None,
    ) -> SearchResult:
        body = _core.build_search_body(category, prompt, params, sort)
        return SearchResult.model_validate(await self._request("POST", "/v1/search", json=body))

    async def categories(self) -> list[Category]:
        return [Category.model_validate(c) for c in await self._request("GET", "/v1/categories")]

    async def usage(self) -> Usage:
        return Usage.model_validate(await self._request("GET", "/v1/usage"))

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncJouyaar:
        return self

    async def __aexit__(self, *exc) -> None:
        await self.aclose()
