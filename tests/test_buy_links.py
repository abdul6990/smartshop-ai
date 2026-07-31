"""Quick direct-link/affiliate-link verification script.

Run:
    python test_buy_links.py
"""

from __future__ import annotations

import os

from utils.affiliate_url_generator import build_purchase_links


def run_demo() -> None:
    # Demo tokens for local validation. These can be removed if .env is already set.
    os.environ.setdefault("AMAZON_ASSOCIATE_TAG", "smartshopaiin-21")

    samples = [
        {
            "name": "Amazon Earbuds",
            "url": "https://www.amazon.in/dp/B0CHX1W1XY",
            "platform": "amazon",
        },
        {
            "name": "Flipkart Laptop Stand",
            "url": "https://www.flipkart.com/laptop-stand/p/itm123",
            "platform": "flipkart",
        },
        {
            "name": "Unknown Source",
            "url": "https://www.example.com/product/abc",
            "platform": None,
        },
    ]

    print("=== Buy Link Verification ===")
    for item in samples:
        result = build_purchase_links(item["url"], platform_hint=item["platform"])
        print(f"\nProduct:            {item['name']}")
        print(f"Detected Platform:  {result['platform']}")
        print(f"Direct Buy URL:     {result['buy_url']}")
        print(f"Affiliate Enabled:  {result['affiliate_enabled']}")
        print(f"Affiliate URL:      {result['affiliate_url']}")


if __name__ == "__main__":
    run_demo()
