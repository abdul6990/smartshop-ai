from tavily import TavilyClient
import os

def run_product_finder(state: dict) -> dict:
    """
    Agent 1: Product Finder
    Searches Amazon India for the product
    and returns structured product data
    """
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    product_name = state["product_name"]

    print(f"\n🔍 Agent 1: Searching Amazon for '{product_name}'...")
    from datetime import datetime
    current_year = datetime.now().year
    # Search 1: Find main product
    main_search = tavily.search(
        query=f"{product_name} price Amazon India {current_year}",
        max_results=5
    )

    # Search 2: Find alternatives
    alt_search = tavily.search(
        query=f"best alternatives to {product_name} Amazon India cheaper",
        max_results=3
    )

    # Format main results
    products_found = []
    for r in main_search["results"]:
        products_found.append({
            "title": r["title"],
            "content": r["content"],
            "url": r["url"]
        })

    # Format alternatives
    alternatives_found = []
    for r in alt_search["results"]:
        alternatives_found.append({
            "title": r["title"],
            "content": r["content"],
            "url": r["url"]
        })

    print(f"✅ Agent 1 done! Found {len(products_found)} results")

    # Put everything in the backpack
    return {
        "products_found": products_found,
        "alternatives_found": alternatives_found,
        "search_query": product_name
    }