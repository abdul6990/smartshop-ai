"""
Cloudscraper-based helper for resilient product page fetching.

This module is optional and can be used by ingestion jobs to reduce blocks while
keeping costs at zero.
"""

from __future__ import annotations

import random
import time
from typing import Dict, Optional

import cloudscraper


class SmartScraper:
    def __init__(self) -> None:
        self.client = cloudscraper.create_scraper()
        self.last_request_by_domain: Dict[str, float] = {}
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        ]

    def _apply_jitter(self, domain: str) -> None:
        delay = random.uniform(2.5, 5.0)
        last_seen = self.last_request_by_domain.get(domain)
        if last_seen is None:
            return

        elapsed = time.time() - last_seen
        if elapsed < delay:
            time.sleep(delay - elapsed)

    def get(self, url: str, domain: str, retries: int = 3) -> Optional[str]:
        for attempt in range(retries):
            self._apply_jitter(domain)
            self.client.headers["User-Agent"] = random.choice(self.user_agents)

            try:
                response = self.client.get(url, timeout=15)
                self.last_request_by_domain[domain] = time.time()

                if response.status_code == 200:
                    return response.text

                if response.status_code in (403, 429):
                    time.sleep(2 ** attempt)
                    continue
            except Exception:
                time.sleep(2 ** attempt)

        return None
