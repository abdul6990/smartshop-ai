"""
Agent 3: Market Analyzer
Detects upcoming sales and market trends
"""
from tavily import TavilyClient
from utils.logger import app_logger
import os
from datetime import datetime

def run_market_analyzer(state: dict) -> dict:
    """
    Agent 3: Market Analyzer
    Finds upcoming sales and market trends
    """
    try:
        product_name = state.get("product_name", "").strip()
        
        if not product_name:
            app_logger.warning("Agent 3: No product name provided")
            return {
                "upcoming_sales": [],
                "product_deals": [],
                "error": "No product name"
            }
        
        app_logger.info(f"Agent 3: Analyzing market for '{product_name}'")
        
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        current_year = datetime.now().year
        
        # Search for upcoming sales
        try:
            sales_search = tavily.search(
                query=f"Amazon India 2026 upcoming sales Prime Day Big Billion Days dates",
                max_results=3
            )
            sales_data = [
                {
                    "title": r["title"],
                    "snippet": r["content"][:300],
                    "url": r["url"]
                }
                for r in sales_search.get("results", [])
            ]
            app_logger.debug(f"Found {len(sales_data)} upcoming sales")
        except Exception as e:
            app_logger.warning(f"Sales search failed: {str(e)}")
            sales_data = []
        
        # Search for product-specific deals
        try:
            deals_search = tavily.search(
                query=f"{product_name} upcoming deal discount Amazon India",
                max_results=3
            )
            deals_data = [
                {
                    "title": r["title"],
                    "snippet": r["content"][:300],
                    "url": r["url"]
                }
                for r in deals_search.get("results", [])
            ]
            app_logger.debug(f"Found {len(deals_data)} product deals")
        except Exception as e:
            app_logger.warning(f"Deals search failed: {str(e)}")
            deals_data = []
        
        app_logger.info("Agent 3 complete")
        
        return {
            "upcoming_sales": sales_data,
            "product_deals": deals_data
        }
        
    except Exception as e:
        app_logger.error(f"Agent 3 error: {str(e)}", exc_info=True)
        return {
            "upcoming_sales": [],
            "product_deals": [],
            "error": str(e)
        }