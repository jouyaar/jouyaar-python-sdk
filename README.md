# Jooyar Python SDK

Official Python client for the **Jooyar (جویار)** agentic search API — compare flights, lodging,
bus, train, retail, and internet plans across Iranian providers from one call.

```bash
pip install jouyaar
```

## Quickstart

```python
from jouyaar import Jooyaar

client = Jooyaar(api_key="sk_live_…")   # or set JOUYAAR_API_KEY

# Structured search — deterministic, LLM-free, cheapest:
res = client.search(
    category="flight",
    params={"origin": "THR", "destination": "MHD", "departure_date": "1404-06-10", "passengers": 1},
    sort="price",
)
for q in res.quotes:
    print(q.provider, f"{q.price_toman:,} تومان", q.plan_name)

# Natural-language search — the API extracts the parameters for you:
res = client.search(category="flight", prompt="ارزان‌ترین پرواز تهران به مشهد فردا صبح")
```

Get a key at **[developers.jouyaar.ir](https://developers.jouyaar.ir)**.

## Two ways to search

| Mode | How | When |
|---|---|---|
| `params=` | structured fields (see `client.categories()`) | you already know the fields — deterministic, no LLM, cheapest |
| `prompt=` | free-text intent | let the API parse a natural-language request |

Pass exactly one. `client.categories()` lists every category and its required/optional fields.

## Async

```python
import asyncio
from jouyaar import AsyncJooyaar

async def main():
    async with AsyncJooyaar() as client:
        res = await client.search(category="lodging",
                                  params={"city": "تهران", "checkin": "1404-06-10", "checkout": "1404-06-12"})
        print(len(res.quotes), "results")

asyncio.run(main())
```

## Errors

All failures raise a `JooyaarError` subclass carrying the server `code` and `request_id`:

```python
import time
from jouyaar import Jooyaar, RateLimitError, QuotaExceededError, AuthenticationError

client = Jooyaar()
try:
    res = client.search(category="flight", prompt="…")
except RateLimitError as e:
    time.sleep(e.retry_after or 1)      # per-minute limit — back off and retry
except QuotaExceededError:
    ...                                  # monthly quota spent — upgrade the plan
except AuthenticationError:
    ...                                  # bad/revoked key
```

`RateLimitError` (429, per-minute) and 5xx responses are **retried automatically** with backoff
(honoring `Retry-After`); 4xx are not. Tune with `Jooyaar(max_retries=..., timeout=...)`.

## Configuration

| Argument | Env var | Default |
|---|---|---|
| `api_key` | `JOUYAAR_API_KEY` | — (required) |
| `base_url` | `JOUYAAR_BASE_URL` | `https://api.jouyaar.ir` |
| `timeout` | — | `30.0` |
| `max_retries` | — | `2` |

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check src tests
```

MIT licensed.
