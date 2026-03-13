from tavily import TavilyClient
import os
import re
from datetime import datetime

def extract_rating(text: str) -> str:
    patterns = [
        r'(\d+\.?\d*)\s*out of\s*5',
        r'(\d+\.?\d*)/5',
        r'(\d+\.?\d*)\s*stars?',
        r'(\d+\.?\d*)\s*★',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            rating = float(match.group(1))
            if 1 <= rating <= 5:
                return f"{rating}★"
    return "N/A"

def extract_price(text: str) -> str:
    patterns = [
        r'₹\s*([\d,]+)',
        r'Rs\.?\s*([\d,]+)',
        r'INR\s*([\d,]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"₹{match.group(1)}"
    return "Check site"

def extract_reviews(text: str) -> str:
    patterns = [
        r'([\d,]+)\s*ratings?',
        r'([\d,]+)\s*reviews?',
        r'([\d,]+)\s*customers?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} reviews"
    return "N/A"

def score_product(product: dict) -> float:
    score = 0
    rating_str = product.get("rating", "N/A")
    if rating_str != "N/A":
        try:
            rating = float(rating_str.replace("★", "").strip())
            score += rating * 8
        except:
            pass
    reviews_str = product.get("reviews", "N/A")
    if reviews_str != "N/A":
        try:
            count = int(reviews_str.replace("reviews", "").replace(",", "").strip())
            score += min(count / 100, 30)
        except:
            pass
    url = product.get("url", "")
    if "/dp/" in url:
        score += 30
    elif "amazon.in" in url and "/s?" not in url:
        score += 15
    elif "amazon.in" in url:
        score += 5
    if "/s?k=" in url or "/s?rh=" in url:
        score -= 20
    return score

def run_product_finder(state: dict) -> dict:
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    product_name = state["product_name"]
    current_year = datetime.now().year

    print(f"\n🔍 Agent 1: Finding best '{product_name}' on Amazon India...")

    try:
        main_search = tavily.search(
            query=f"{product_name} buy Amazon India price rating reviews {current_year}",
            max_results=7,
            search_depth="advanced"
        )
        alt_search = tavily.search(
            query=f"best alternatives to {product_name} Amazon India budget",
            max_results=4
        )
    except Exception as e:
        print(f"❌ Tavily search failed: {e}")
        return {
            "products_found": [],
            "alternatives_found": [],
            "best_product": {},
            "search_query": product_name
        }

    products_found = []
    seen_urls = set()

    for r in main_search["results"]:
        url = r.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        content = r.get("content", "")
        product = {
            "title": r.get("title", ""),
            "url": url,
            "price": extract_price(content),
            "rating": extract_rating(content),
            "reviews": extract_reviews(content),
            "summary": content[:200] + "..." if len(content) > 200 else content
        }
        products_found.append(product)

    products_found.sort(key=score_product, reverse=True)
    best_product = products_found[0] if products_found else {}

    alternatives_found = []
    for r in alt_search["results"]:
        content = r.get("content", "")
        alternatives_found.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "price": extract_price(content),
            "rating": extract_rating(content),
            "summary": content[:150] + "..." if len(content) > 150 else content
        })

    print(f"✅ Agent 1 done! Found {len(products_found)} products")
    if best_product:
        print(f"🏆 Best: {best_product['title'][:50]} | {best_product.get('rating')} | {best_product.get('price')}")

    return {
        "products_found": products_found[:5],
        "alternatives_found": alternatives_found[:3],
        "best_product": best_product,
        "search_query": product_name
    }