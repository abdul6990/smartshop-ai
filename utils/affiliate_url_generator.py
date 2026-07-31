"""Utilities for generating affiliate URLs from direct product links."""

from __future__ import annotations

import os
from typing import Optional, Tuple, TypedDict
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_PLATFORM_ALIASES = {
    "flipkart": "flipkart",
    "amazon": "amazon",
    "ebay": "ebay",
}


class PurchaseLinks(TypedDict):
    buy_url: str
    affiliate_url: Optional[str]
    affiliate_enabled: bool
    platform: str


def infer_platform(product_url: str, platform_hint: Optional[str] = None) -> str:
    """Infer platform from hint or URL host.

    Returns one of: flipkart, amazon, ebay, unknown
    """
    if platform_hint:
        normalized = platform_hint.strip().lower()
        if normalized in _PLATFORM_ALIASES:
            return _PLATFORM_ALIASES[normalized]

    host = urlparse(product_url).netloc.lower()
    if "flipkart" in host:
        return "flipkart"
    if "amazon" in host:
        return "amazon"
    if "ebay" in host:
        return "ebay"
    return "unknown"


def _set_query_param(url: str, key: str, value: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query[key] = value
    return urlunparse(
        parsed._replace(query=urlencode(query, doseq=True))
    )


def _get_env_token(platform: str) -> Optional[str]:
    if platform == "flipkart":
        return os.getenv("FLIPKART_AFFILIATE_ID")
    if platform == "amazon":
        return os.getenv("AMAZON_ASSOCIATE_TAG") or os.getenv("AMAZON_AFFILIATE_ID")
    if platform == "ebay":
        return os.getenv("EBAY_CAMPAIGN_ID") or os.getenv("EBAY_AFFILIATE_ID")
    return None


def generate_affiliate_url(
    product_url: str,
    platform_hint: Optional[str] = None,
    affiliate_token: Optional[str] = None,
) -> Tuple[str, bool]:
    """Generate affiliate URL.

    Returns:
    - affiliate_url
    - enabled flag
    """
    platform = infer_platform(product_url, platform_hint)
    token = affiliate_token or _get_env_token(platform)

    if not token:
        return product_url, False

    if platform == "flipkart":
        return _set_query_param(product_url, "affid", token), True
    if platform == "amazon":
        return _set_query_param(product_url, "tag", token), True
    if platform == "ebay":
        return _set_query_param(product_url, "campid", token), True

    return product_url, False


def build_purchase_links(
    product_url: str,
    platform_hint: Optional[str] = None,
) -> PurchaseLinks:
    """Build direct and affiliate links for recommendation payloads."""
    affiliate_url, enabled = generate_affiliate_url(
        product_url=product_url,
        platform_hint=platform_hint,
    )
    return {
        "buy_url": product_url,
        "affiliate_url": affiliate_url if enabled else None,
        "affiliate_enabled": enabled,
        "platform": infer_platform(product_url, platform_hint),
    }
