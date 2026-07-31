"""
Agent 1: Product Finder
Searches for products on multiple e-commerce platforms
"""
import asyncio
from tavily import TavilyClient
from utils.logger import app_logger
from utils.validators import validate_product_name
import os
import re
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from agents.smart_scraper_cloudscraper import SmartScraper

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-IN,en;q=0.9',
}

SMART_SCRAPER = SmartScraper()

def extract_product_name_from_url(url: str) -> str:
    """Extract product name from Amazon/Flipkart URL"""
    try:
        # Amazon: amazon.in/Product-Name-Here/dp/ASIN
        amazon_match = re.search(r'amazon\.in/([^/]+)/dp/', url)
        if amazon_match:
            name = amazon_match.group(1).replace('-', ' ')
            return name[:80]

        # Flipkart: flipkart.com/product-name/p/...
        flipkart_match = re.search(r'flipkart\.com/([^/]+)/p/', url)
        if flipkart_match:
            name = flipkart_match.group(1).replace('-', ' ')
            return name[:80]

        # Meesho
        meesho_match = re.search(r'meesho\.com/([^/]+)/p/', url)
        if meesho_match:
            name = meesho_match.group(1).replace('-', ' ')
            return name[:80]
    except:
        pass
    return ""

def fetch_real_price(url: str, query: str = "") -> dict:
    """Fetch actual price from product page"""
    try:
        domain = "amazon.in" if "amazon" in url else "flipkart.com" if "flipkart" in url else "generic"
        html = SMART_SCRAPER.get(url, domain=domain)

        # Fallback to plain requests if cloudscraper path fails.
        if not html:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            html = resp.text

        price = "Check site"
        rating = "N/A"
        title = ""

        # Amazon price patterns
        if 'amazon' in url:
            # Price
            for pattern in [
                r'<span class="a-price-whole">([\d,]+)',
                r'"priceAmount":([\d.]+)',
                r'<span id="priceblock_ourprice"[^>]*>₹\s*([\d,]+)',
            ]:
                m = re.search(pattern, html)
                if m:
                    price_num = int(m.group(1).replace('.','').replace(',',''))
                    # Validate price is reasonable
                    min_p, max_p = get_price_range_for_product(query)
                    if min_p <= price_num <= max_p:
                        price = f"₹{price_num:,}"
                    break

            # Rating
            m = re.search(r'(\d+\.?\d*) out of 5 stars', html)
            if m: rating = f"{m.group(1)}★"

            # Title
            m = re.search(r'<span id="productTitle"[^>]*>\s*([^<]+)', html)
            if m: title = m.group(1).strip()[:100]

        # Flipkart price patterns
        elif 'flipkart' in url:
            for pattern in [
                r'₹([\d,]+)</div><div class="[^"]*">MRP',
                r'"finalPrice":([\d]+)',
                r'class="_30jeq3[^"]*">₹([\d,]+)',
            ]:
                m = re.search(pattern, html)
                if m:
                    price_num = int(m.group(1).replace(',',''))
                    # Validate price is reasonable
                    min_p, max_p = get_price_range_for_product(query)
                    if min_p <= price_num <= max_p:
                        price = f"₹{price_num:,}"
                    break

            m = re.search(r'"averageRating":([\d.]+)', html)
            if m: rating = f"{m.group(1)}★"

            m = re.search(r'class="B_NuCI">([^<]+)', html)
            if m: title = m.group(1).strip()[:100]

        # Meesho price patterns
        elif 'meesho' in url:
            m = re.search(r'"price":([\d]+)', html)
            if m:
                price_num = int(m.group(1))
                # Validate price
                min_p, max_p = get_price_range_for_product(query)
                if min_p <= price_num <= max_p:
                    price = f"₹{price_num:,}"

        return {"price": price, "rating": rating, "title": title}

    except Exception as e:
        print(f"Fetch failed for {url}: {e}")
        return {"price": "Check site", "rating": "N/A", "title": ""}

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

def get_price_range_for_product(query: str) -> tuple:
    """Get min and max price range based on product type"""
    query_lower = query.lower()
    
    # Check for laptops
    is_laptop = any(w in query_lower for w in ['macbook', 'laptop', 'notebook', 'chromebook'])
    if is_laptop:
        return (20000, 500000)
    
    # Check for mobile devices / smartphones
    mobile_keywords = [
        'iphone', 'moto', 'motorola', 'samsung', 'redmi', 'realme', 
        'oneplus', 'vivo', 'oppo', 'xiaomi', 'pixel', 'nothing', 
        'iqoo', 'poco', 'phone', 'mobile', 'smartphone', 'galaxy'
    ]
    if any(k in query_lower for k in mobile_keywords):
        return (5000, 250000)
    
    # Check for tablets
    if any(word in query_lower for word in ['tablet', 'ipad']):
        return (6000, 200000)
        
    # Check for watches / wearables
    if any(word in query_lower for word in ['watch', 'smartwatch']):
        return (1000, 100000)
        
    # Audio products
    if any(word in query_lower for word in ['headphones', 'earbuds', 'earphone', 'airpods', 'headset', 'audio']):
        return (500, 60000)

    # General fallback range
    return (500, 200000)

def extract_price_from_text(text: str, query: str = "") -> str:
    """Extract price with pattern matching, EMI filtering, and category validation"""
    if not text:
        return "Check site"
        
    # Filter out EMI / per month lines first
    lines = text.split('\n')
    clean_lines = [
        l for l in lines 
        if not any(e in l.lower() for e in ['/month', 'per month', 'emi starts', 'starting emi', 'every month'])
    ]
    clean_text = ' '.join(clean_lines) if clean_lines else text

    patterns = [
        r'₹\s*([0-9,]+(?:\.[0-9]{2})?)',  # ₹1,234 or ₹1,234.56
        r'Rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)',  # Rs 1,234
        r'INR\s*([0-9,]+(?:\.[0-9]{2})?)',  # INR 1,234
        r'Price:\s*([0-9,]+)',  # Price: 1234
        r'\$\s*([0-9,]+(?:\.[0-9]{2})?)',  # $100
    ]
    
    is_emi_context = any(word in text.lower() for word in ['emi', 'starting', 'starts', 'per month', '/month'])
    min_price, max_price = get_price_range_for_product(query)
    
    for pattern in patterns:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        if matches:
            prices = []
            for match in matches:
                try:
                    clean = match.replace(',', '').split('.')[0]
                    p = int(clean)
                    prices.append(p)
                except:
                    pass
            
            if prices:
                valid_prices = [p for p in prices if min_price <= p <= max_price]
                
                if valid_prices:
                    # If EMI context, choose higher price (full device price instead of monthly EMI)
                    selected_price = max(valid_prices) if is_emi_context and len(valid_prices) > 1 else min(valid_prices)
                    return f"₹{selected_price:,}"
    
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

def get_platform(url: str) -> str:
    if 'amazon' in url: return 'Amazon'
    if 'flipkart' in url: return 'Flipkart'
    if 'meesho' in url: return 'Meesho'
    if 'myntra' in url: return 'Myntra'
    if 'snapdeal' in url: return 'Snapdeal'
    if 'jiomart' in url: return 'JioMart'
    if 'nykaa' in url: return 'Nykaa'
    if 'ajio' in url: return 'Ajio'
    return 'Web'

def is_indian_shopping_site(url: str) -> bool:
    """Check if URL is from an Indian shopping site"""
    indian_domains = [
        'amazon.in', 'flipkart.com', 'meesho.com', 'myntra.com',
        'snapdeal.com', 'jiomart.com', 'nykaa.com', 'ajio.com',
        'paytmmall.com', 'shopclues.com', 'craftsvilla.com',
        'limeroad.com', 'voonik.com', 'tokopedia.com'
    ]
    url_lower = url.lower()
    
    # Must be from Indian site
    if not any(domain in url_lower for domain in indian_domains):
        return False
    
    # Exclude western domains even if they appear in URL
    western_sites = ['bestbuy', 'walmart', 'target', 'ebay.com', 'amazon.com', 'newegg']
    if any(site in url_lower for site in western_sites):
        return False
    
    return True

def score_product(product: dict) -> float:
    """
    Score product based on multiple factors:
    - Rating (40 points) - higher is better
    - Review count (30 points) - more reviews = more reliable
    - Price (20 points) - lower is better
    - Platform trust (10 points) - Amazon/Flipkart more trusted
    """
    score = 0
    
    # 1. Rating Score (0-40 points)
    rating_str = product.get("rating", "N/A")
    if rating_str != "N/A" and rating_str:
        try:
            rating = float(rating_str.replace("★", "").strip())
            if 1 <= rating <= 5:
                score += (rating / 5) * 40  # Normalize to 40 points
        except:
            pass
    
    # 2. Review Count Score (0-30 points)
    reviews_str = product.get("reviews", "N/A")
    if reviews_str != "N/A" and reviews_str:
        try:
            count_str = reviews_str.replace(" reviews", "").replace(" reviews", "").replace(",", "").strip()
            count = int(float(count_str))
            # More reviews = higher score, capped at 30 points
            review_score = min(count / 1000, 30)  # 1000 reviews = max score
            score += review_score
        except:
            pass
    
    # 3. Price Score (0-20 points) - lower price is better
    price_str = product.get("price", "Check site")
    if price_str != "Check site":
        try:
            price_num = int(price_str.replace("₹", "").replace(",", "").strip())
            # Lower price = higher score
            # Price scoring: 0-20k = 20 points, scales down
            if price_num < 20000:
                score += 20
            elif price_num < 50000:
                score += 15
            elif price_num < 100000:
                score += 10
            else:
                score += 5
        except:
            pass
    
    # 4. Platform Trust Score (0-10 points)
    platform = product.get("platform", "").lower()
    platform_scores = {
        "amazon": 10,
        "flipkart": 10,
        "myntra": 8,
        "meesho": 6,
        "snapdeal": 6,
        "jiomart": 7,
    }
    score += platform_scores.get(platform, 3)
    
    # 5. Seller badge boost (if mentioned)
    title_lower = product.get("title", "").lower()
    if "best seller" in title_lower:
        score += 5
    
    # 6. Accessory Penalty (CRITICAL)
    # Penalize accessories that might show up in main product searches
    accessory_keywords = [
        "case", "cover", "back cover", "tempered glass", "screen protector", 
        "guard", "film", "skin", "pouch", "adapter", "cable", "charger",
        "earphones", "refurbished", "pre-owned", "adapter", "lens protector",
        "bag", "backpack", "sleeve", "stand", "mount", "holder", "strap",
        "dock", "hub", "splitter", "converter", "protector", "mat", "pad"
    ]
    if any(k in title_lower for k in accessory_keywords):
        app_logger.info(f"⚠️ Accessory detected in: {title_lower[:30]} - Applying penalty")
        score -= 60  # Heavy penalty to ensure they don't outrank actual devices
    
    return score

def safe_search(tavily, query: str, max_results: int = 3) -> list:
    try:
        result = tavily.search(query=query, max_results=max_results)
        return result.get("results", [])
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def run_product_finder(state: dict) -> dict:
    """
    Agent 1: Product Finder - Comprehensive Search
    Searches across all platforms and returns TOP 5 best products
    """
    try:
        product_input = state.get("product_name", "").strip()
        
        if not product_input:
            app_logger.error("Empty product name")
            return {
                "products_found": [],
                "best_5_products": [],
                "search_query": "",
                "error": "Product name required"
            }
        
        app_logger.info(f"Agent 1: Comprehensive search for '{product_input}'")

        # Primary discovery path uses Tavily web search; ProductScraper remains
        # a documented fallback/mock utility outside the main pipeline.
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        current_year = datetime.now().year
        
        # Comprehensive search queries across all major platforms
        search_queries = [
            # Amazon India
            f"{product_input} amazon.in best {current_year}",
            f"{product_input} site:amazon.in",
            
            # Flipkart
            f"{product_input} flipkart best price {current_year}",
            f"{product_input} site:flipkart.com",
            
            # Myntra (fashion)
            f"{product_input} myntra",
            
            # Meesho
            f"{product_input} meesho",
            
            # Direct shopping queries
            f"best {product_input} buy online India",
            f"{product_input} lowest price online",
            f"{product_input} best seller India",
            f"{product_input} review rating best",
        ]
        
        all_products = []
        seen_urls = set()
        
        # Search across all queries
        for query in search_queries:
            try:
                results = tavily.search(query=query, max_results=5)
                for r in results.get("results", []):
                    url = r.get("url", "")
                    content = r.get("content", "")
                    title = r.get("title", "")
                    
                    # Filter: Skip search result pages, get product detail pages
                    if url and url not in seen_urls:
                        # Exclude search pages
                        if any(skip in url for skip in ['/s?', 's?q=', '/search', '/find']):
                            continue
                        
                        # INDIA FILTER: Only include Indian shopping sites
                        if not is_indian_shopping_site(url):
                            app_logger.debug(f"⏭️ Skipping non-Indian site: {url[:50]}")
                            continue
                        
                        seen_urls.add(url)
                        
                        product = {
                            "title": title[:120],
                            "url": url,
                            "platform": get_platform(url),
                            "price": extract_price_from_text(content, product_input),
                            "rating": extract_rating(content),
                            "reviews": extract_reviews(content),
                            "description": content[:200]
                        }
                        
                        # Score the product
                        product["score"] = score_product(product)
                        all_products.append(product)
                        
                        app_logger.debug(f"Found: {product['title'][:50]} | Score: {product['score']:.1f}")
                        
            except Exception as e:
                app_logger.warning(f"Query failed: {query[:50]} - {str(e)}")
                continue
        
        # Sort by score (highest first) and get top candidates for verification
        sorted_products = sorted(all_products, key=lambda p: p.get("score", 0), reverse=True)
        top_candidates = sorted_products[:8]
        
        # Real-time verification for top candidates
        verified_products = []
        for p in top_candidates:
            if p["price"] == "Check site":
                app_logger.info(f"🔍 Verifying price for: {p['title'][:30]}...")
                real_data = fetch_real_price(p["url"], product_input)
                if real_data["price"] != "Check site":
                    p["price"] = real_data["price"]
                if real_data["rating"] != "N/A":
                    p["rating"] = real_data["rating"]
                if real_data["title"]:
                    p["title"] = real_data["title"]
            
            # Re-score after verification
            p["score"] = score_product(p)
            verified_products.append(p)

        # Final sort and select Top 5
        final_products = sorted(verified_products, key=lambda p: p.get("score", 0), reverse=True)[:5]
        
        app_logger.info(f"Agent 1 complete: Found {len(sorted_products)} total, {len(final_products)} verified")
        for i, p in enumerate(final_products, 1):
            app_logger.info(f"  #{i}: {p['title'][:50]} | {p['platform']} | {p['price']} | {p['rating']} | Score: {p['score']:.1f}")
        
        return {
            "products_found": final_products,
            "best_5_products": final_products,
            "all_products": sorted_products[:10],
            "search_query": product_input,
            "total_found": len(sorted_products)
        }
        
    except Exception as e:
        app_logger.error(f"Agent 1 error: {str(e)}", exc_info=True)
        return {
            "products_found": [],
            "best_5_products": [],
            "search_query": state.get("product_name", ""),
            "error": str(e)
        }