"""
Agent 2: Price Historian
Finds price history and current best deals
"""
from tavily import TavilyClient
from utils.logger import app_logger
import os

def run_price_historian(state: dict) -> dict:
    """
    Agent 2: Price Historian
    Searches for price history and current best deals
    """
    try:
        product_name = state.get("product_name", "").strip()
        
        if not product_name:
            app_logger.warning("Agent 2: No product name provided")
            return {
                "price_history": [],
                "best_price_data": [],
                "error": "No product name"
            }
        
        app_logger.info(f"Agent 2: Checking price history for '{product_name}'")
        
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # Search for price history
        try:
            history_search = tavily.search(
                query=f"{product_name} price history lowest price ever India",
                max_results=3
            )
            history_data = [
                {
                    "title": r["title"],
                    "snippet": r["content"][:300],
                    "url": r["url"]
                }
                for r in history_search.get("results", [])
            ]
            app_logger.debug(f"Found {len(history_data)} price history results")
        except Exception as e:
            app_logger.warning(f"Price history search failed: {str(e)}")
            history_data = []
        
        # Search for best current prices
        try:
            best_price_search = tavily.search(
                query=f"{product_name} best price today Amazon India discount offer",
                max_results=3
            )
            best_price_data = [
                {
                    "title": r["title"],
                    "snippet": r["content"][:300],
                    "url": r["url"]
                }
                for r in best_price_search.get("results", [])
            ]
            app_logger.debug(f"Found {len(best_price_data)} best price results")
        except Exception as e:
            app_logger.warning(f"Best price search failed: {str(e)}")
            best_price_data = []
        
        app_logger.info("Agent 2 complete")
        
        return {
            "price_history": history_data,
            "best_price_data": best_price_data
        }
        
    except Exception as e:
        app_logger.error(f"Agent 2 error: {str(e)}", exc_info=True)
        return {
            "price_history": [],
            "best_price_data": [],
            "error": str(e)
        }