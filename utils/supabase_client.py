"""
Supabase Client for Database Operations

Thin client providing connection management and table access.
All business logic lives in dedicated service modules:
  - utils/product_service.py
  - utils/wishlist_service.py
    - utils/auth.py
  - agents/price_tracker.py
  - agents/recommendation_engine.py
"""
import os
from supabase import create_client, Client
from utils.logger import app_logger
from typing import Optional


class SupabaseDB:
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")

        if not self.url or not self.key:
            app_logger.warning("⚠️  Supabase credentials not configured — API will use fallbacks")
            self.client: Optional[Client] = None
        else:
            try:
                self.client = create_client(self.url, self.key)
                app_logger.info("✅ Supabase connected")
            except Exception as e:
                app_logger.error(f"Supabase connection failed: {e}")
                self.client = None

    # ────────── Connection helpers ──────────

    @property
    def is_connected(self) -> bool:
        """Check whether the Supabase client is initialised."""
        return self.client is not None

    def table(self, table_name: str):
        """Proxy method to access a Supabase table.

        Raises if the client is not configured — callers should
        either guard with ``is_connected`` or handle the exception.
        """
        if not self.client:
            raise Exception(
                "Supabase not configured. "
                "Set SUPABASE_URL and SUPABASE_KEY in your .env file."
            )
        return self.client.table(table_name)

    def health_check(self) -> dict:
        """Quick connectivity test against the platforms table."""
        if not self.is_connected:
            return {"status": "disconnected", "message": "Supabase credentials not set"}
        try:
            result = self.table("platforms").select("name").limit(1).execute()
            return {
                "status": "connected",
                "message": f"OK — {len(result.data or [])} platform(s) found",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global singleton
db = SupabaseDB()
