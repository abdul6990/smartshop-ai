from tavily import TavilyClient
import os

def run_market_analyzer(state: dict) -> dict:
    """
    Agent 3: Market Analyzer
    Finds upcoming Amazon sales events
    and market trends for the product
    """
    from datetime import datetime
    current_year = datetime.now().year
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    product_name = state["product_name"]

    print(f"\n📰 Agent 3: Analyzing market for '{product_name}'...")

    # Search 1: Upcoming Amazon sales
    sales_search = tavily.search(
        query="Amazon India upcoming sale {current_year} Big Billion Days Prime Day dates",
        max_results=3
    )
    
    # Search 2: Product specific deals
    deals_search = tavily.search(
        query=f"{product_name} upcoming deal discount Amazon India {current_year}",
        max_results=3
    )

    sales_data = []
    for r in sales_search["results"]:
        sales_data.append({
            "title": r["title"],
            "content": r["content"],
            "url": r["url"]
        })

    deals_data = []
    for r in deals_search["results"]:
        deals_data.append({
            "title": r["title"],
            "content": r["content"],
            "url": r["url"]
        })

    print(f"✅ Agent 3 done!")

    return {
        "upcoming_sales": sales_data,
        "product_deals": deals_data
    }