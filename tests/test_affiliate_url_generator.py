"""Quick verification script for affiliate URL generation."""

from __future__ import annotations

import os

from utils.affiliate_url_generator import build_purchase_links


def seed_demo_tokens() -> None:
    # Demo-only values so the script works before real account approvals.
    os.environ.setdefault("FLIPKART_AFFILIATE_ID", "demoFlipkart123")
    os.environ.setdefault("AMAZON_ASSOCIATE_TAG", "smartshop-21")
    os.environ.setdefault("EBAY_CAMPAIGN_ID", "demoEbay999")


def main() -> None:
    seed_demo_tokens()

    samples = [
        ("https://www.flipkart.com/apple-iphone-15/p/itm123", "flipkart"),
        ("https://www.amazon.in/dp/B0CHX1W1XY", "amazon"),
        ("https://www.ebay.com/itm/1234567890", "ebay"),
        ("https://www.example.com/product/abc", None),
    ]

    print("Testing affiliate URL generation\n")
    for product_url, platform in samples:
        result = build_purchase_links(product_url, platform_hint=platform)
        print(f"Input URL:       {product_url}")
        print(f"Platform:        {result['platform']}")
        print(f"Direct buy URL:  {result['buy_url']}")
        print(f"Affiliate URL:   {result['affiliate_url']}")
        print(f"Enabled:         {result['affiliate_enabled']}")
        print("-" * 72)


if __name__ == "__main__":
    main()
