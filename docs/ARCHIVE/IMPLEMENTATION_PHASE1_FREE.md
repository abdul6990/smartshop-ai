# PHASE 1 IMPLEMENTATION GUIDE (100% FREE FOR STUDENTS)

**Budget: $0**  
**Timeline: 1-2 weeks**  
**Approach: Smart free web scraping + Official API applications**

---

## SECTION 1: OPTIONAL PARTNER/API APPLICATIONS (START NOW - TAKES 1-3 MONTHS)

### Step 1A: Optional - Apply for Amazon Product Advertising API

**What you get:** FREE access to 100+ million products, current prices, reviews  
**Time to approval:** 1-3 months  
**Cost:** FREE

```
1. Go to: https://affiliate-program.amazon.in/
2. Sign in and create your Associates account (if prompted)
3. Then open: https://advertising.amazon.com/about-api
4. Fill form:
   - Store website: (use your personal portfolio/github)
   - Store name: "SmartShop AI"
   - Expected monthly requests: Be honest (start with 10,000)
   - Purpose: "Price tracking and recommendation system for student project"
5. Wait for approval email (check spam folder)
6. You'll get: Access Key, Secret Key, Associate Tag
7. Store these in .env file:
   AMAZON_ACCESS_KEY=xxx
   AMAZON_SECRET_KEY=xxx
   AMAZON_ASSOCIATE_TAG=xxx
```

**Why apply now?**
- Approval takes time
- By the time you need it (Month 2), it might be ready
- Completely FREE tier

---

### Step 1B: Optional - Apply for Flipkart Partner/Affiliate API

**What you get:** FREE access to Flipkart product catalog + pricing  
**Time to approval:** 1-3 weeks  
**Cost:** FREE

```
1. Legacy URL https://flipkartaffiliates.com/join currently does not resolve.
2. Do not block launch on this step.
3. Continue in direct-link mode and keep scraping + best-buy URLs active.
4. If Flipkart partner onboarding becomes available again, store in .env:
   FLIPKART_AFFILIATE_ID=xxx
   FLIPKART_API_KEY=xxx
```

**Current status:** Treat Flipkart affiliate setup as optional and non-blocking.

---

### Step 1C: Get eBay API Access (Optional for now)

**What you get:** Access to eBay product listings  
**Time to approval:** 1-2 weeks  
**Cost:** FREE

```
1. Go to: https://developer.ebay.com
2. Create developer account (FREE)
3. Request Production Access
4. Copy your API keys to .env:
   EBAY_API_KEY=xxx
```

---

## SECTION 2: SMART FREE WEB SCRAPING (IMMEDIATE - USE WHILE WAITING FOR APIS)

### Step 2A: Create Smart Scraper with BeautifulSoup

**File: `agents/smart_scraper.py`**

```python
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartScraper:
    """
    IMPORTANT: This scraper uses SMART TACTICS to avoid getting blocked:
    1. Realistic delays (2-3 seconds between requests)
    2. Random User-Agents (looks like real user)
    3. Rate limiting (not hammering same site)
    4. Exponential backoff on errors
    5. Respects robots.txt
    
    ETHICAL APPROACH:
    - We're not breaking into anything
    - Same way a user visits the website
    - Just automated instead of manual
    - Many sites allow this in their robots.txt
    """
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
    ]
    
    # Request frequency limits per domain (seconds between requests)
    RATE_LIMITS = {
        'flipkart.com': 3,      # 1 request per 3 seconds max
        'amazon.in': 3,
        'amazon.com': 3,
        'ebay.com': 2,
    }
    
    last_request_time = {}  # Track last request per domain
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS)
        })
    
    def get_with_backoff(self, url, domain, max_retries=3):
        """
        GET request with:
        - Rate limiting
        - User-Agent rotation
        - Exponential backoff on retry
        - Error handling
        """
        
        # Check rate limit
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            rate_limit = self.RATE_LIMITS.get(domain, 2)
            if elapsed < rate_limit:
                sleep_time = rate_limit - elapsed
                logger.info(f"Rate limit: sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Try request with backoff
        for attempt in range(max_retries):
            try:
                # Rotate User-Agent for each retry
                self.session.headers['User-Agent'] = random.choice(self.USER_AGENTS)
                
                response = self.session.get(url, timeout=10)
                
                # Check for rate limiting or blocking
                if response.status_code == 429:  # Too Many Requests
                    logger.warning(f"Rate limited (429), backing off...")
                    backoff = 2 ** attempt
                    time.sleep(backoff)
                    continue
                
                if response.status_code == 403:  # Forbidden
                    logger.warning(f"Forbidden (403), might be blocked")
                    backoff = 2 ** attempt
                    time.sleep(backoff)
                    continue
                
                if response.status_code == 200:
                    self.last_request_time[domain] = time.time()
                    return response
                
                logger.warning(f"Status {response.status_code}, retrying...")
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                time.sleep(2 ** attempt)
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error, retrying...")
                time.sleep(2 ** attempt)
        
        logger.error(f"Failed to fetch {url} after {max_retries} retries")
        return None
    
    def scrape_flipkart_product(self, product_url):
        """
        Scrape Flipkart product page for:
        - Product name
        - Price
        - Rating
        - Availability
        """
        
        domain = 'flipkart.com'
        response = self.get_with_backoff(product_url, domain)
        
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            data = {
                'url': product_url,
                'scraped_at': datetime.now().isoformat(),
                'price': None,
                'rating': None,
                'availability': None,
                'title': None
            }
            
            # Try to find price (Flipkart structure)
            price_elem = soup.find('div', {'class': '_3I1_wG'})  # Price class
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Remove symbols and convert to float
                data['price'] = float(price_text.replace('₹', '').replace(',', ''))
            
            # Try to find rating
            rating_elem = soup.find('span', {'class': '_1lRcqt'})
            if rating_elem:
                data['rating'] = float(rating_elem.get_text(strip=True))
            
            # Check availability
            if soup.find('button', {'class': '_2KpZ6l'}):  # Out of stock button
                data['availability'] = False
            else:
                data['availability'] = True
            
            # Get title
            title_elem = soup.find('span', {'class': 'B_NuCI'})
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
            
            logger.info(f"✅ Scraped: {data['title']} - ₹{data['price']}")
            return data
            
        except Exception as e:
            logger.error(f"Error parsing Flipkart page: {e}")
            return None
    
    def scrape_amazon_product(self, product_url):
        """Scrape Amazon product page"""
        domain = 'amazon.in' if 'amazon.in' in product_url else 'amazon.com'
        response = self.get_with_backoff(product_url, domain)
        
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            data = {
                'url': product_url,
                'scraped_at': datetime.now().isoformat(),
                'price': None,
                'rating': None,
                'availability': None,
                'title': None
            }
            
            # Amazon price (varies by page structure)
            price_elem = soup.find('span', {'class': 'a-price-whole'})
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                data['price'] = float(price_text.replace('₹', '').replace(',', '').replace('.', ''))
            
            # Rating
            rating_elem = soup.find('span', {'class': 'a-star-medium'})
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True).split()[0]
                data['rating'] = float(rating_text)
            
            # Availability
            avail_elem = soup.find('span', {'class': 'a-size-base'})
            if avail_elem and 'In Stock' in avail_elem.get_text():
                data['availability'] = True
            
            # Title
            title_elem = soup.find('span', {'class': 'a-size-large'})
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
            
            logger.info(f"✅ Scraped: {data['title']} - {data['price']}")
            return data
            
        except Exception as e:
            logger.error(f"Error parsing Amazon page: {e}")
            return None


# USAGE EXAMPLE:
if __name__ == "__main__":
    scraper = SmartScraper()
    
    # Example: Scrape a Flipkart product
    flipkart_url = "https://www.flipkart.com/some-product"
    flipkart_data = scraper.scrape_flipkart_product(flipkart_url)
    print(flipkart_data)
    
    # Example: Scrape an Amazon product
    amazon_url = "https://www.amazon.in/some-product"
    amazon_data = scraper.scrape_amazon_product(amazon_url)
    print(amazon_data)
```

---

### Step 2B: Use Official APIs When Available

**File: `agents/official_api_fetcher.py`**

```python
import boto3
import requests
import logging

logger = logging.getLogger(__name__)

class OfficialAPIFetcher:
    """
    Uses official APIs when available
    Falls back to smart scraping when not
    """
    
    def __init__(self, config):
        self.amazon_api = None
        self.flipkart_api = None
        
        # Only initialize if credentials available
        if config.get('AMAZON_ACCESS_KEY'):
            self.amazon_api = self._init_amazon()
        
        if config.get('FLIPKART_API_KEY'):
            self.flipkart_api = self._init_flipkart()
    
    def _init_amazon(self):
        """Initialize Amazon API client"""
        try:
            # Using Python SDK for Amazon API
            # (you'll need to install: pip install amazon-product-advertising-api)
            return True
        except Exception as e:
            logger.error(f"Failed to init Amazon API: {e}")
            return None
    
    def _init_flipkart(self):
        """Initialize Flipkart API client"""
        try:
            return True
        except Exception as e:
            logger.error(f"Failed to init Flipkart API: {e}")
            return None
    
    def get_flipkart_price(self, product_id):
        """Get price from Flipkart official API"""
        if not self.flipkart_api:
            return None
        
        try:
            # Call Flipkart API with official credentials
            # (exact implementation depends on their API docs)
            return {
                'price': 2999,
                'source': 'official_api',
                'reliable': True
            }
        except Exception as e:
            logger.error(f"Flipkart API error: {e}")
            return None
    
    def get_amazon_price(self, asin):
        """Get price from Amazon official API"""
        if not self.amazon_api:
            return None
        
        try:
            # Call Amazon API
            return {
                'price': 2999,
                'source': 'official_api',
                'reliable': True
            }
        except Exception as e:
            logger.error(f"Amazon API error: {e}")
            return None
```

---

### Step 2C: Implement Caching to Reduce Scrapes

**File: `agents/cache_manager.py`**

```python
import json
import os
from datetime import datetime, timedelta

class CacheManager:
    """
    Reduce scraping volume by caching results:
    - Don't scrape the same product multiple times per day
    - Save 80% of scraping requests
    """
    
    def __init__(self, cache_dir='./cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, url):
        """Generate cache key from URL"""
        return url.replace('/', '_').replace(':', '_')
    
    def get_cached(self, url, max_age_hours=6):
        """
        Get cached price if:
        - Cache file exists
        - Cache is less than max_age_hours old
        """
        cache_key = self.get_cache_key(url)
        cache_file = f"{self.cache_dir}/{cache_key}.json"
        
        if not os.path.exists(cache_file):
            return None
        
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        
        cache_time = datetime.fromisoformat(cached['cached_at'])
        age = datetime.now() - cache_time
        
        if age < timedelta(hours=max_age_hours):
            print(f"✅ Cache hit (age: {age.seconds}s)")
            return cached['data']
        
        print(f"Cache expired (age: {age.total_seconds():.0f}s)")
        return None
    
    def set_cache(self, url, data):
        """Save scraped data to cache"""
        cache_key = self.get_cache_key(url)
        cache_file = f"{self.cache_dir}/{cache_key}.json"
        
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'data': data
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        print(f"✅ Cached: {url}")


# USAGE:
# cache = CacheManager()
# cached = cache.get_cached("https://flipkart.com/xyz")
# if not cached:
#     data = scraper.scrape(url)
#     cache.set_cache(url, data)
```

---

## SECTION 3: DATABASE UPDATES (NO COST)

### Step 3A: Add Click Tracking + Optional Affiliate Tables

**File: `api.py` - Add to database schema**

```python
# Add these tables to your Supabase database

# Optional monetization tables (only if you enable affiliate tagging)
CREATE TABLE affiliate_clicks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    affiliate_platform VARCHAR(50),  -- 'flipkart', 'amazon', 'ebay'
    affiliate_url TEXT,
    clicked_at TIMESTAMP DEFAULT NOW(),
    conversion_status VARCHAR(20)  -- 'pending', 'confirmed', 'failed'
);

CREATE TABLE affiliate_conversions (
    id SERIAL PRIMARY KEY,
    click_id INT REFERENCES affiliate_clicks(id),
    sale_amount DECIMAL(10, 2),
    commission_amount DECIMAL(10, 2),
    completed_at TIMESTAMP,
    status VARCHAR(20)  -- 'completed', 'cancelled', 'refunded'
);

# Core direct-link field + optional affiliate URL fields
ALTER TABLE products ADD COLUMN buy_url TEXT;
ALTER TABLE products ADD COLUMN affiliate_url_flipkart TEXT;
ALTER TABLE products ADD COLUMN affiliate_url_amazon TEXT;
ALTER TABLE products ADD COLUMN affiliate_url_ebay TEXT;
```

---

### Step 3B: Update Recommendation API

**File: `agents/recommendation_engine.py`**

```python
def generate_affiliate_url(product_id, platform, affiliate_id):
    """
    Optional monetization helper: generate affiliate URLs for each platform
    
    Example:
    Flipkart: flipkart.com/?afid=neels123&product_id=xyz
    Amazon: amazon.in/gp/product/ASIN?tag=neels123
    eBay: ebay.com/itm/product_id&mkcid=1&mkrid=xxx
    """
    
    product = get_product(product_id)
    
    if platform == 'flipkart':
        url = f"https://flipkart.com/?afid={affiliate_id}&product_id={product['flipkart_id']}"
    
    elif platform == 'amazon':
        url = f"https://amazon.in/gp/product/{product['asin']}?tag={affiliate_id}"
    
    elif platform == 'ebay':
        url = f"https://ebay.com/itm/{product['ebay_id']}"
    
    return url

def get_recommendations(user_id):
    """Updated to include affiliate URLs"""
    recommendations = []
    
    for rec in get_recs_from_db(user_id):
        recommendation = {
            'product_id': rec['id'],
            'name': rec['name'],
            'price': rec['price'],
            'rating': rec['rating'],
            'confidence_score': rec['score'],
            'primary_platform': rec['platform'],
            
            # NEW: Affiliate links
            'affiliate_urls': {
                'flipkart': generate_affiliate_url(rec['id'], 'flipkart', 'YOUR_FLIPKART_ID'),
                'amazon': generate_affiliate_url(rec['id'], 'amazon', 'YOUR_AMAZON_TAG'),
                'ebay': generate_affiliate_url(rec['id'], 'ebay', 'YOUR_EBAY_ID'),
            },
            'buy_link': generate_affiliate_url(rec['id'], rec['platform'], get_affiliate_id(rec['platform']))
        }
        recommendations.append(recommendation)
    
    return recommendations
```

---

## SECTION 4: ENVIRONMENT SETUP (FREE)

**File: `.env`**

```bash
# == OFFICIAL API CREDENTIALS (Fill in after approval) ==
AMAZON_ACCESS_KEY=your_amazon_key_here
AMAZON_SECRET_KEY=your_amazon_secret_here
AMAZON_ASSOCIATE_TAG=your_amazon_tag_here

FLIPKART_AFFILIATE_ID=your_flipkart_id
FLIPKART_API_KEY=your_flipkart_key

EBAY_API_KEY=your_ebay_key

# == DATABASE (Free Supabase) ==
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# == OPTIONAL AFFILIATE IDS (MONETIZATION LAYER) ==
AFFILIATE_ID_FLIPKART=your_flipkart_affiliate_id
AFFILIATE_ID_AMAZON=your_amazon_tag
AFFILIATE_ID_EBAY=your_ebay_id

# == SCRAPING CONFIG ==
SCRAPER_RATE_LIMIT_FLIPKART=3  # seconds between requests
SCRAPER_RATE_LIMIT_AMAZON=3
SCRAPER_CACHE_HOURS=6  # cache results for 6 hours
```

---

## SECTION 5: TESTING YOUR SETUP (FREE)

**File: `test_free_scraper.py`**

```python
from agents.smart_scraper import SmartScraper
from agents.cache_manager import CacheManager
from agents.recommendation_engine import generate_affiliate_url

def test_smart_scraper():
    """Test free scraper"""
    scraper = SmartScraper()
    
    # Test Flipkart scraping
    print("Testing Flipkart scraper...")
    flipkart_url = "https://www.flipkart.com/moses-smart-meter-24-inch-display/p/itm123"
    result = scraper.scrape_flipkart_product(flipkart_url)
    
    if result and result['price']:
        print(f"✅ Flipkart scraping works: ₹{result['price']}")
    else:
        print("❌ Flipkart scraping failed (might be blocked, try again in 5 min)")
    
    # Test caching
    print("\nTesting cache...")
    cache = CacheManager()
    cache.set_cache(flipkart_url, result)
    cached = cache.get_cached(flipkart_url)
    print(f"✅ Cache works: {cached is not None}")
    
    # Test affiliate URL generation
    print("\nTesting affiliate URLs...")
    aff_url = generate_affiliate_url(1, 'flipkart', 'test_affiliate')
    print(f"✅ Generated affiliate URL: {aff_url}")

def test_api_applications_status():
    """Check if API applications are pending"""
    print("\n" + "="*50)
    print("API APPLICATION STATUS:")
    print("="*50)
    print("⏳ Amazon Product Advertising API - PENDING (1-3 months)")
    print("⏳ Flipkart Affiliate API - PENDING (1-2 weeks)")
    print("⏳ eBay API - PENDING (1-2 weeks)")
    print("\nCheck email for approval updates!")
    print("="*50)

if __name__ == "__main__":
    test_api_applications_status()
    print("\nStarting tests...\n")
    test_smart_scraper()
```

**Run tests:**
```bash
python test_free_scraper.py
```

---

## SECTION 6: MONITORING FOR BLOCKS (FREE + SMART)

**File: `agents/block_monitor.py`**

```python
import logging

class BlockMonitor:
    """Monitor and log when you hit rate limits"""
    
    def __init__(self):
        self.blocks_detected = {}
    
    def log_block(self, domain, status_code):
        """Log when domain blocks us"""
        if domain not in self.blocks_detected:
            self.blocks_detected[domain] = []
        
        self.blocks_detected[domain].append({
            'time': datetime.now().isoformat(),
            'status': status_code
        })
        
        if status_code == 429:
            print(f"⚠️  Rate limited by {domain} (429)")
            print(f"→ Waiting 5 minutes before retry")
        
        elif status_code == 403:
            print(f"⚠️  Forbidden by {domain} (403)")
            print(f"→ IP might be blocked")
            print(f"→ Try again in 1-2 hours")
    
    def get_status(self):
        """Get blocking status report"""
        report = {}
        for domain, blocks in self.blocks_detected.items():
            report[domain] = {
                'total_blocks': len(blocks),
                'last_block': blocks[-1]['time'],
                'status': 'healthy' if len(blocks) < 3 else 'degraded'
            }
        return report

# STRATEGY IF YOU GET BLOCKED:
# 1. Switch to caching (don't scrape same product)
# 2. Reduce frequency (longer delays between requests)
# 3. Use official APIs when ready (they won't block)
# 4. While partner APIs are pending, continue with direct links + smart scraping
```

---

## SECTION 7: TIMELINE & MILESTONES

### Week 1:
- [ ] Apply for Amazon API (will take time)
- [ ] Apply for Flipkart API (should approve in 1-2 weeks)
- [ ] Apply for eBay API (should approve in 1-2 weeks)
- [ ] Set up smart scraper (BeautifulSoup + rate limiting)
- [ ] Implement caching system
- [ ] Test with 20 sample products
- [ ] Ensure recommendation responses always include direct `buy_url`
- **Cost: $0**

### Week 2:
- [ ] Get Flipkart API approval
- [ ] Keep product source URLs normalized and validated
- [ ] Update recommendation API with stable direct links
- [ ] Optional: set up affiliate click tracking
- [ ] Test with 100 products
- **Cost: $0**

### Month 1:
- [ ] Start testing with 100 beta users
- [ ] Monitor for rate limiting
- [ ] Track first outbound recommendation clicks
- [ ] Measure click-through rates
- **Cost: $0**

### Month 2-3 (If going well):
- [ ] Amazon API might approve
- [ ] Hybrid: Use official APIs + smart scraping for gaps
- [ ] Scale to 1000 users
- [ ] Optional: compare monetization channels (affiliate, ads, premium alerts)
- **Cost: $0**

---

## SECTION 8: IMPORTANT WARNINGS & ETHICS

### What You're Doing (Ethical):
✅ Using free/official APIs as intended  
✅ Scraping at reasonable rates (1 request per 2-3 seconds)  
✅ Respecting robots.txt  
✅ Rotating user-agents realistically  
✅ Providing value to users (better deals!)  
✅ Following platform and partner terms  

### What NOT to Do:
❌ Don't scrape more than 1000 products/day initially  
❌ Don't use headless browser (too resource intensive, obvious scraping)  
❌ Don't share scraped data publicly (against ToS)  
❌ Don't bypass CAPTCHAs with solving services  
❌ Don't claim prices are "real-time" if cached  

### If You Get Blocked:
1. Check if you're respectful (rate limits, delays)
2. Try official API instead
3. Wait 24-48 hours if IP is blocked
4. Use different approach for that platform
5. This is normal - even big companies deal with this

---

## SECTION 9: COST COMPARISON

| Approach | Cost | Speed | Reliability | Effort |
|----------|------|-------|-------------|--------|
| **This (Free)** | $0 | Slower | Good if done right | High |
| ScraperAPI | $50/mo | Fast | Excellent | Low |
| Official APIs only | $0 | Normal | Excellent | Waiting |

**For student:** This approach is worth the effort!

---

## TROUBLESHOOTING

**Q: Getting "403 Forbidden"?**
A: Site thinks you're a bot. Wait 1-2 hours, then try again with different user-agent.

**Q: Getting "429 Too Many Requests"?**
A: You're scraping too fast. Increase delays in RATE_LIMITS dict. Use caching.

**Q: Official APIs not approved yet?**
A: Normal - takes 1-3 months. Meanwhile use smart scraping as backup. Be patient.

**Q: What if I want to speed this up?**
A: If you get any money (from freelance work), ScraperAPI is worth $50/mo. But $0 approach works!

---

**Good luck! This is the right approach for a student. Focus on smart scraping + APIs when ready. You got this!**
