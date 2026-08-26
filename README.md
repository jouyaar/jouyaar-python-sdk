# Jooyar Python SDK

[![PyPI](https://img.shields.io/pypi/v/jouyaar.svg)](https://pypi.org/project/jouyaar/)
[![Python](https://img.shields.io/pypi/pyversions/jouyaar.svg)](https://pypi.org/project/jouyaar/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Official Python client for the **Jooyar (جویار)** agentic search API — compare flights, lodging,
bus, train, retail, and internet plans across Iranian providers from one call.

```bash
pip install jouyaar
# or, with uv:
uv add jouyaar
```

```python
from jouyaar import Jooyaar

client = Jooyaar(api_key="sk_live_…")   # or set JOUYAAR_API_KEY

res = client.search(category="flight", prompt="ارزان‌ترین پرواز تهران به مشهد فردا صبح")
for q in res.quotes:
    print(q.provider, f"{q.price_toman:,} تومان", q.plan_name)
```

## Features

- Sync (`Jooyaar`) and async (`AsyncJooyaar`) clients
- Structured (`params=`) or natural-language (`prompt=`) search
- Typed errors and automatic retry with backoff on 429/5xx
- Fully type-hinted, Pydantic models

## Documentation

Get an API key and read the full docs at **[developers.jouyaar.ir](https://developers.jouyaar.ir)**.

MIT licensed.
