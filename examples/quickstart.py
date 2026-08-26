"""Quickstart — set JOUYAAR_API_KEY (and JOUYAAR_BASE_URL for a non-prod host), then run:

    uv run --with . python examples/quickstart.py
"""

from jouyaar import Jouyaar, RateLimitError


def main() -> None:
    with Jouyaar() as client:  # reads JOUYAAR_API_KEY
        print("Plan/usage:", client.usage())

        print("\nCategories:")
        for cat in client.categories():
            required = [f.name for f in cat.fields if f.required]
            print(f"  - {cat.name} ({cat.fa_title}) required={required}")

        # Structured (LLM-free) search — cheapest, deterministic.
        try:
            res = client.search(
                category="flight",
                params={"origin": "THR", "destination": "MHD", "departure_date": "1404-06-10", "passengers": 1},
                sort="price",
            )
        except RateLimitError as e:
            print(f"rate limited; retry after {e.retry_after}s")
            return

        print(f"\nSearch ok={res.ok} — {len(res.quotes)} quotes")
        for q in res.quotes[:5]:
            print(f"  {q.provider:12} {q.price_toman:>12,} تومان  {q.plan_name}")


if __name__ == "__main__":
    main()
