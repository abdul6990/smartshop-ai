"""
IMPLEMENTATION GUIDE: ScraperAPI + Direct-Link Integration
Phase 1: Web Scraping & Price Intelligence Foundation
"""

================================================================================
STEP 1: SCRAPERAPI SETUP & INTEGRATION
================================================================================

1A. Create ScraperAPI Account:
   URL: https://www.scraperapi.com
   - Sign up for free (50 requests free)
   - Upgrade to paid plan ($50/month for 3,000 requests)
   - Get your API key from dashboard

1B. Install ScraperAPI Python Client:
   $ pip install scraperapi-sdk

1C. Create agents/scraper_config.py:

```python
import os
from scraperapi import ScraperAPIClient

# Configuration
SCRAPER_API_KEY = os.getenv('SCRAPER_API_KEY')
SCRAPER_CLIENT = ScraperAPIClient(api_key=SCRAPER_API_KEY)

# Supported platforms
PLATFORMS = {
    'flipkart': {
        'base_url': 'https://www.flipkart.com',
        'affiliate_id': os.getenv('FLIPKART_AFFILIATE_ID'),  # optional
        'commission_rate': 0.04,
        'search_pattern': '/search?q='
    },
    'amazon': {
        'base_url': 'https://www.amazon.in',
        'affiliate_id': os.getenv('AMAZON_AFFILIATE_ID'),  # optional
        'commission_rate': 0.03,
        'search_pattern': '/s?k='
    },
    'ebay': {
        'base_url': 'https://www.ebay.com',
        'affiliate_id': os.getenv('EBAY_AFFILIATE_ID'),  # optional
        'commission_rate': 0.01,
        'search_pattern': '/sch/i.html?_nkw='
    }
}

def get_scraper_url(platform, url):
    """Get ScraperAPI formatted URL"""
    return f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={url}"

def create_affiliate_url(platform, product_url, product_id):
    """Create affiliate link (optional monetization layer)"""
    platform_info = PLATFORMS.get(platform)
    if platform == 'flipkart':
        return f"{product_url}?afid={platform_info['affiliate_id']}&pid={product_id}"
    elif platform == 'amazon':
        return f"{product_url}?tag={platform_info['affiliate_id']}"
    elif platform == 'ebay':
        return f"{product_url}?campid={platform_info['affiliate_id']}"
    return product_url
```

1D. Update agents/price_tracker.py:

```python
from scraperapi import ScraperAPIClient
from agents.scraper_config import SCRAPER_CLIENT, PLATFORMS, create_affiliate_url
import requests
from bs4 import BeautifulSoup

class ScrapedPriceTracker:
    @staticmethod
    def scrape_product_price(product_url, platform):
        """Scrape price using ScraperAPI"""
        try:
            # Use ScraperAPI to get page content
            response = requests.get(
                f"http://api.scraperapi.com?api_key={os.getenv('SCRAPER_API_KEY')}&url={product_url}"
            )
            
            if response.status_code != 200:
                raise Exception(f"Scrape failed: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Platform-specific parsing
            if platform == 'flipkart':
                price = extract_flipkart_price(soup)
            elif platform == 'amazon':
                price = extract_amazon_price(soup)
            elif platform == 'ebay':
                price = extract_ebay_price(soup)
            else:
                raise ValueError(f"Unknown platform: {platform}")
            
            return {
                'price': price,
                'platform': platform,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            print(f"Scraper error for {product_url}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def extract_flipkart_price(soup):
        """Extract price from Flipkart HTML"""
        price_elem = soup.find('div', {'class': '_30jeq3'})
        if price_elem:
            price_text = price_elem.get_text().strip()
            # Remove ₹ and commas: "₹1,299" → 1299
            price = float(price_text.replace('₹', '').replace(',', ''))
            return price
        raise ValueError("Could not extract Flipkart price")
    
    @staticmethod
    def extract_amazon_price(soup):
        """Extract price from Amazon HTML"""
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            price_text = price_elem.get_text().strip()
            price = float(price_text.replace('₹', '').replace(',', '').split('.')[0])
            return price
        raise ValueError("Could not extract Amazon price")
    
    @staticmethod
    def extract_ebay_price(soup):
        """Extract price from eBay HTML"""
        price_elem = soup.find('span', {'class': 'POSITIVE'})
        if price_elem:
            price_text = price_elem.get_text().strip()
            price = float(price_text.replace('$', '').replace(',', ''))
            return price
        raise ValueError("Could not extract eBay price")
```

================================================================================
STEP 2: BUY URL SETUP (AFFILIATE OPTIONAL)
================================================================================

2A. Configure Direct Buy URLs (Required):

Store each product's source platform URL in your database and expose it as
`buy_url` in recommendations. This keeps the system fully functional even if
affiliate programs are unavailable.

2B. Optional: Register for Affiliate Programs (Monetization Layer):

FLIPKART:
    - URL: Legacy portal https://flipkartaffiliates.com (currently not resolving)
  - Commission: 3-5% (Electronics/Fashion)
  - Steps:
        1. Do not block launch on this portal
        2. Continue with direct `buy_url` mode
        3. If onboarding reopens, add to .env: FLIPKART_AFFILIATE_ID=neels1234

AMAZON ASSOCIATES:
    - URL: https://affiliate-program.amazon.in/
  - Commission: 2-4% (category dependent)
  - Steps:
    1. Sign up with valid ID
    2. Wait for approval (1-2 weeks)
    3. Get associate tag (looks like: "neels01-21")
    4. Add to .env: AMAZON_AFFILIATE_ID=neels01-21

EBAY PARTNER NETWORK:
  - URL: https://ebaypartnernetwork.com
  - Commission: 1-3%
  - Steps:
    1. Sign up
    2. Create campaign ID
    3. Add to .env: EBAY_CAMPAIGN_ID=xxxxx

2C. Update recommendations API response:

```python
# api.py

@app.get("/api/recommendations/personalized")
async def get_personalized_recommendations(user_id: str):
    """Get personalized product recommendations with direct buy links"""
    try:
        recommendation = RecommendationEngine.generate_recommendations(user_id)
        
        # Add direct buy URLs to each recommendation
        for rec in recommendation.recommendations:
            product = db.table('products').select('*').eq('id', rec.product_id).execute()
            if product.data:
                platform = product.data[0].get('primary_platform', 'flipkart')
                product_url = product.data[0].get('url')
                rec.buy_url = product_url
                
                # Optional monetization: create affiliate link when IDs are configured
                affiliate_url = create_affiliate_url(
                    platform=platform,
                    product_url=product_url,
                    product_id=rec.product_id
                )
                rec.affiliate_url = affiliate_url
        
        # Save recommendation for later tracking
        RecommendationEngine.save_recommendation(recommendation)
        
        return recommendation.dict()
        
    except Exception as e:
        logger.error(f"Error in get_personalized_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

2D. Optional: Create affiliate tracking:

```python
# utils/affiliate_tracker.py

from datetime import datetime
from utils.supabase_client import db

class AffiliateTracker:
    @staticmethod
    def track_click(user_id, product_id, platform, affiliate_url):
        """Track when user clicks affiliate link"""
        db.table('affiliate_clicks').insert({
            'user_id': user_id,
            'product_id': product_id,
            'platform': platform,
            'affiliate_url': affiliate_url,
            'clicked_at': datetime.now().isoformat()
        }).execute()
    
    @staticmethod
    def track_conversion(click_id, purchase_amount, commission_earned):
        """Track successful purchase"""
        db.table('affiliate_conversions').insert({
            'click_id': click_id,
            'purchase_amount': purchase_amount,
            'commission_earned': commission_earned,
            'converted_at': datetime.now().isoformat()
        }).execute()
    
    @staticmethod
    def get_click_through_rate(user_id, period_days=30):
        """Calculate CTR"""
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=period_days)).isoformat()
        
        clicks = db.table('affiliate_clicks')\
            .select('count', count='exact')\
            .eq('user_id', user_id)\
            .gte('clicked_at', start_date)\
            .execute()
        
        conversions = db.table('affiliate_conversions')\
            .select('count', count='exact')\
            .gte('converted_at', start_date)\
            .execute()
        
        total_clicks = clicks.count or 0
        total_conversions = conversions.count or 0
        
        ctr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        return {
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'ctr_percent': ctr
        }
    
    @staticmethod
    def get_monthly_revenue():
        """Get total revenue from affiliates"""
        from datetime import datetime, timedelta
        
        start_date = (datetime.now().replace(day=1)).isoformat()
        
        revenue = db.table('affiliate_conversions')\
            .select('commission_earned')\
            .gte('converted_at', start_date)\
            .execute()
        
        total = sum(r['commission_earned'] for r in revenue.data or [])
        return total
```

================================================================================
STEP 3: DATABASE UPDATES
================================================================================

3A. Optional: Add affiliate tracking tables:

```sql
-- affiliate_clicks table
CREATE TABLE affiliate_clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    product_id VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    affiliate_url TEXT NOT NULL,
    clicked_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- affiliate_conversions table
CREATE TABLE affiliate_conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    click_id UUID NOT NULL,
    purchase_amount DECIMAL(10,2) NOT NULL,
    commission_earned DECIMAL(10,2) NOT NULL,
    converted_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (click_id) REFERENCES affiliate_clicks(id)
);

-- Indexes for performance
CREATE INDEX idx_affiliate_clicks_user_id ON affiliate_clicks(user_id);
CREATE INDEX idx_affiliate_clicks_clicked_at ON affiliate_clicks(clicked_at);
CREATE INDEX idx_affiliate_conversions_converted_at ON affiliate_conversions(converted_at);
```

3B. Update products table:

```sql
ALTER TABLE products ADD COLUMN buy_url TEXT;
ALTER TABLE products ADD COLUMN primary_platform VARCHAR DEFAULT 'flipkart';
ALTER TABLE products ADD COLUMN amazon_url TEXT;
ALTER TABLE products ADD COLUMN flipkart_url TEXT;
ALTER TABLE products ADD COLUMN ebay_url TEXT;
ALTER TABLE products ADD COLUMN affiliate_url TEXT; -- optional
```

================================================================================
STEP 4: ENVIRONMENT SETUP
================================================================================

4A. Update .env file:

```
# ScraperAPI Configuration
SCRAPER_API_KEY=your_scraperapi_key_here

# Optional Affiliate IDs (Monetization Layer)
FLIPKART_AFFILIATE_ID=your_flipkart_id
AMAZON_AFFILIATE_ID=your_amazon_tag
EBAY_CAMPAIGN_ID=your_ebay_campaign_id

# API Keys
FLIPKART_API_KEY=optional_flipkart_api_key
AMAZON_API_KEY=optional_amazon_api_key

# Scraping Configuration
SCRAPE_INTERVAL_HOURS=6
SCRAPE_TIMEOUT_SECONDS=30
MAX_RETRIES=3
```

================================================================================
STEP 5: TESTING & VERIFICATION
================================================================================

5A. Test ScraperAPI integration:

```python
# test_scraper.py

from agents.scraper_config import SCRAPER_CLIENT
from agents.price_tracker import ScrapedPriceTracker

def test_flipkart_scraper():
    """Test scraping Flipkart product"""
    product_url = "https://www.flipkart.com/realme-12-pro-5g/p/itm123456"
    result = ScrapedPriceTracker.scrape_product_price(product_url, 'flipkart')
    
    assert result['success'] == True
    assert result['price'] > 0
    assert result['platform'] == 'flipkart'
    print(f"✅ Flipkart scraper works: ₹{result['price']}")

def test_amazon_scraper():
    """Test scraping Amazon product"""
    product_url = "https://www.amazon.in/dp/B0934K5C3L"
    result = ScrapedPriceTracker.scrape_product_price(product_url, 'amazon')
    
    assert result['success'] == True
    assert result['price'] > 0
    print(f"✅ Amazon scraper works: ₹{result['price']}")

def test_affiliate_link_generation():
    """Test affiliate URL creation"""
    from agents.scraper_config import create_affiliate_url
    
    url = "https://www.flipkart.com/product123"
    affiliate_url = create_affiliate_url('flipkart', url, 'prod_123')
    
    assert 'afid=' in affiliate_url
    assert os.getenv('FLIPKART_AFFILIATE_ID') in affiliate_url
    print(f"✅ Affiliate URL generation works: {affiliate_url}")

if __name__ == '__main__':
    test_flipkart_scraper()
    test_amazon_scraper()
    test_affiliate_link_generation()
    print("\n✅ All integration tests passed!")
```

================================================================================
STEP 6: MONITORING & DASHBOARD
================================================================================

6A. Add monitoring endpoint:

```python
# api.py

@app.get("/api/admin/affiliate-stats")
async def get_affiliate_stats(period_days: int = 30):
    """Get affiliate performance stats"""
    from utils.affiliate_tracker import AffiliateTracker
    
    # Get total revenue
    total_revenue = AffiliateTracker.get_monthly_revenue()
    
    # Get individual platform stats
    platforms_stats = {}
    for platform in ['flipkart', 'amazon', 'ebay']:
        clicks = db.table('affiliate_clicks')\
            .select('count', count='exact')\
            .eq('platform', platform)\
            .execute()
        
        platforms_stats[platform] = {
            'clicks': clicks.count or 0,
            'platform': platform
        }
    
    return {
        'total_revenue': total_revenue,
        'period_days': period_days,
        'platforms': platforms_stats,
        'timestamp': datetime.now().isoformat()
    }
```

================================================================================
NEXT STEPS:
================================================================================

1. Set up ScraperAPI account (5 minutes)
2. Confirm product `buy_url` storage and API response fields (30 minutes)
3. Update .env file (5 minutes)
4. Run database migrations (10 minutes)
5. Test scrapers (30 minutes)
6. Deploy and monitor (ongoing)

EXPECTED OUTCOMES:
✅ Can reliably scrape Flipkart/Amazon
✅ Generate direct buy links automatically
✅ Track recommendation quality and click intent
✅ Monitor revenue in real-time
✅ Scale to 10k users without IP blocks

TIMELINE: Complete this implementation in Week 1-2
COST: $50/month (ScraperAPI), affiliate optional
REVENUE: Optional affiliate layer can be added after core model stabilizes

================================================================================
