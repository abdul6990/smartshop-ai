from tavily import TavilyClient
import os

def run_price_historian(state: dict) -> dict:
    """
    Agent 2: Price Historian
    Searches for price history and 
    cheapest available price right now
    """
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    product_name = state["product_name"]

    print(f"\n📊 Agent 2: Checking price history for '{product_name}'...")

    # Search 1: Price history
    history_search = tavily.search(
        query=f"{product_name} price history lowest price ever Amazon India",
        max_results=3
    )

    # Search 2: Current best price
    best_price_search = tavily.search(
        query=f"{product_name} best price today Amazon India discount offer",
        max_results=3
    )

    history_data = []
    for r in history_search["results"]:
        history_data.append({
            "title": r["title"],
            "content": r["content"],
            "url": r["url"]
        })

    best_price_data = []
    for r in best_price_search["results"]:
        best_price_data.append({
            "title": r["title"],
            "content": r["content"],
            "url": r["url"]
        })

    print(f"✅ Agent 2 done!")

    return {
        "price_history": history_data,
        "best_price_data": best_price_data
    }