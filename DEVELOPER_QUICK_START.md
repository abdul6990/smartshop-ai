# SmartShop AI - Quick Reference & Developer Guide

## 🎯 SYSTEM AT A GLANCE

**What it does:** 5-agent AI system that finds real deals on Indian e-commerce platforms  
**Tech stack:** FastAPI + LangGraph + Cohere + Tavily + Supabase + React Native  
**Target users:** Price-conscious Indian shoppers  
**Status:** Production-ready ✅

---

## 🚀 QUICK START (5 MINUTES)

### Option 1: Docker (Recommended)
```bash
docker-compose up --build
# API ready at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

### Option 2: Local Development
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Test the API
```bash
# Health check
curl http://localhost:8000/api/health

# Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Main search endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 14 Pro",
    "user_email": "user@example.com"
  }'
```

---

## 📊 DATA FLOW: USER REQUEST TO RESPONSE

```
1. User: POST /api/analyze with product name
   ↓
2. FastAPI validates input & checks cache
   ↓
3. Invokes LangGraph pipeline (8-15 seconds)
   ↓
4. Agent 1 (Product Finder):
   - Search Tavily for products
   - Scrape real prices from Amazon, Flipkart, Meesho
   - Score & rank by price, rating, platform
   - Output: 5-50 products sorted
   ↓
5. Agent 2 (Price Historian):
   - Search historical prices
   - Find lowest prices ever
   - Identify seasonal patterns
   - Output: Price history context
   ↓
6. Agent 3 (Market Analyzer):
   - Find upcoming sales (Prime Day, etc.)
   - Product-specific deals
   - Market trends
   - Output: Deal opportunities
   ↓
7. Agent 4 (AI Predictor):
   - Aggregate all data
   - Call Cohere LLM
   - Generate: BUY/WAIT recommendation
   - Output: AI prediction + timing advice
   ↓
8. Agent 5 (Alert Manager):
   - Save to database
   - Create price alert
   - Send email/WhatsApp
   - Output: Tracking confirmation
   ↓
9. Return to user:
   - TOP 5 products
   - AI prediction
   - Tracking status
   ↓
10. Cache result for 5 minutes
```

---

## 🤖 THE 5 AGENTS EXPLAINED

### Agent 1: Product Finder 🔍
**Purpose:** Discover products  
**Input:** "iPhone 14 Pro"  
**Output:** [List of 50+ products with prices & ratings]  
**Technology:** Tavily API + CloudScraper  
**Key code:** [agents/product_finder.py](agents/product_finder.py) `run_product_finder()`

```python
# What it does:
1. Search Tavily for products
2. Extract URL, price, rating, platform
3. Scrape real prices from product pages
4. Score each product (0-100):
   - Price competitiveness (40%)
   - Rating normalization (30%)
   - Platform reputation (20%)
   - Stock availability (10%)
5. Return top 5-50 sorted by score
```

---

### Agent 2: Price Historian 📊
**Purpose:** Find price history & deals  
**Input:** Product name, current products  
**Output:** [Price history data, best deals]  
**Technology:** Tavily API  
**Key code:** [agents/price_historian.py](agents/price_historian.py) `run_price_historian()`

```python
# What it does:
1. Search Tavily for historical prices
2. Find lowest price ever recorded
3. Identify price drop patterns
4. Find current best prices
5. Return snippets for user context
```

---

### Agent 3: Market Analyzer 📈
**Purpose:** Identify upcoming sales & trends  
**Input:** Product name, price history  
**Output:** [Upcoming sales, product deals]  
**Technology:** Tavily API  
**Key code:** [agents/market_analyzer.py](agents/market_analyzer.py) `run_market_analyzer()`

```python
# What it does:
1. Search for Amazon Prime Day dates
2. Search for Flipkart Big Billion Days
3. Find product-specific deals
4. Look for clearance/seasonal sales
5. Return opportunities for better prices
```

---

### Agent 4: AI Predictor 🧠
**Purpose:** Price forecasting & recommendations  
**Input:** ALL previous agent outputs  
**Output:** AI prediction (BUY/WAIT + reason)  
**Technology:** LangChain + Cohere LLM  
**Key code:** [agents/ai_predictor.py](agents/ai_predictor.py) `run_ai_predictor()`

```python
# What it does:
1. Aggregate: products, prices, history, sales, deals
2. Create Cohere prompt with all context
3. LLM analyzes and generates recommendation:
   - CURRENT PRICE: ₹X
   - HISTORICAL LOW: ₹Y (Dec 2024)
   - BUY OR WAIT: [with confidence %]
   - BEST TIME: Prime Day (estimated June)
4. Return natural language recommendation
```

**Sample Output:**
```
iPhone 14 Pro Analysis:
- Current Price: ₹79,999 (Amazon)
- Historical Low: ₹72,500 (December 2024)
- Recommendation: WAIT (60% confidence)
- Best Time: Amazon Prime Day (early June)
- Reasoning: Last Prime Day showed 10-15% discounts.
  Wait 2-3 weeks for likely 12-15% drop.
- Alternative: Flipkart has ₹77,999 today (better deal)
```

---

### Agent 5: Alert Manager 🔔
**Purpose:** Save tracking & send alerts  
**Input:** Best product, AI prediction, user email  
**Output:** Tracking confirmation  
**Technology:** Supabase + Gmail + Twilio  
**Key code:** [agents/alert_manager.py](agents/alert_manager.py) `run_alert_manager()`

```python
# What it does:
1. Create alert record in DB
2. Save to tracked_products.json
3. Send email notification
4. Send WhatsApp alert (if enabled)
5. Return success confirmation

# Alert triggered when:
- Price drops below target (e.g., ₹75,000)
- Significant sale found (>10% discount)
- Historical low reached
```

---

## 📡 API ENDPOINTS QUICK REFERENCE

### Authentication (Passwordless OTP)
```
POST /api/auth/request-otp
├─ Input: { "email": "user@example.com" }
└─ Output: { "success": true, "message": "OTP sent" }

POST /api/auth/verify-otp
├─ Input: { "email": "user@example.com", "otp": "123456" }
└─ Output: { "success": true, "user_id": "abc-123", "session_token": "..." }
```

### Main Analysis (5-Agent Pipeline)
```
POST /api/analyze ⭐ MAIN ENDPOINT
├─ Input: { "product_name": "iPhone 14 Pro", "user_email": "user@example.com" }
└─ Output: {
    "success": true,
    "total_found": 47,
    "best_5_products": [{
      "title": "Apple iPhone 14 Pro 128GB",
      "price": "₹79,999",
      "rating": "4.5★",
      "platform": "Amazon India",
      "score": 94.5,
      "buy_url": "https://amazon.in/...",
      "badge": "Best Deal"
    }, ...],
    "ai_prediction": "Recommendation: WAIT until Prime Day...",
    "alert_status": "✅ iPhone 14 Pro now being tracked!",
    "best_product": {...}
  }
```

### Dashboard & Tracking
```
GET /api/dashboard/{user_id}
└─ Returns: { stats: { total_tracked: 5, total_saved: ₹15,000 }, recent_activity: [...] }

GET /api/wishlist/{user_id}
└─ Returns: { success: true, wishlist: [...], total: 5 }

GET /api/price-alerts
└─ Returns: { success: true, alerts: [{...}, ...] }
```

### Full endpoint list: See README.md (19 endpoints total)

---

## 💾 DATABASE QUICK REFERENCE

### Key Tables
```
users              → User accounts + preferences
products           → Product info (name, brand, image, rating)
product_prices     → Price history (tracks price on each platform daily)
wishlists          → User's tracked products
wishlist_items     → Items in wishlist with target prices
price_alerts       → Active price threshold alerts
otp_verifications  → OTP codes for passwordless login
platforms          → E-commerce retailers (Amazon, Flipkart, etc.)
categories         → Product categories (Smartphones, Laptops, etc.)
```

### Query Examples
```sql
-- Get best price for product across all platforms
SELECT product_id, platform_id, MIN(price) as lowest_price
FROM product_prices
WHERE product_id = 'abc-123'
GROUP BY product_id, platform_id;

-- Get user's items with recent price drops
SELECT wi.product_name, wi.price_when_added, wp.price as current_price
FROM wishlist_items wi
JOIN product_prices wp ON wi.product_id = wp.product_id
WHERE wi.wishlist_id = 'xyz-456'
AND wp.price < (wi.price_when_added * 0.9);  -- 10% drop

-- Trending deals (biggest recent drops)
SELECT product_id, COUNT(*) as drop_count
FROM price_alerts
WHERE created_at > NOW() - INTERVAL 7 days
GROUP BY product_id
ORDER BY COUNT(*) DESC
LIMIT 10;
```

---

## 🔐 AUTHENTICATION FLOW

### How OTP Works
```
1. User enters email → POST /api/auth/request-otp
2. Backend generates 6-digit OTP (e.g., "123456")
3. Stores in otp_verifications table + in-memory cache
4. Sets expiry: 10 minutes from now
5. Sends email via Gmail SMTP
6. User receives: "Your OTP: 123456 (expires in 10 min)"
7. User enters OTP → POST /api/auth/verify-otp
8. Backend checks:
   - Is it valid? (in memory or DB)
   - Has it expired? (now < expires_at)
   - Was it already used? (security check)
9. If valid:
   - Mark OTP as used (prevent replay)
   - Create/update user in users table
   - Generate session token
   - Return user_id to frontend
10. Frontend stores token in AsyncStorage
11. All future requests include: Authorization: Bearer <user_id>
```

### Getting an OTP
```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

Response:
{
  "success": true,
  "message": "OTP sent to test@example.com",
  "expires_in_seconds": 600
}
```

### Verifying OTP
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com", "otp":"123456"}'

Response:
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_token": "550e8400-e29b-41d4-a716-446655440000"
}

# Now use in all requests:
# Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000
```

---

## ⚡ CACHING STRATEGY

### When Results Are Cached
```
GET /api/dashboard/{user_id}     → Cached for 2 minutes
GET /api/deals                   → Cached for 5 minutes  
GET /api/recommendations/*       → Cached for 10 minutes
POST /api/analyze (if same query) → Cached for 5 minutes
```

### Cache Invalidation
```python
# Automatic (when data changes):
- User adds to wishlist → Invalidate dashboard cache
- New price recorded → Invalidate deals cache
- User profile updated → Invalidate recommendations cache

# Manual (in code):
cache.delete(key)              # Delete one entry
cache.clear()                  # Clear all cache
cache_invalidate(prefix="dashboard")  # Clear by prefix
```

### Fallback Strategy
```
Cache Layer 1: Redis (production)
  └─ If available, use Redis (fast, shared)
  └─ Key: {prefix}_{identifier}
  └─ TTL: expires automatically

Cache Layer 2: In-Memory (development/fallback)
  └─ If Redis unavailable, use memory dict
  └─ Custom expiry tracking
  └─ No external dependency
```

---

## 🧪 TESTING THE SYSTEM

### Run All Tests
```bash
pytest tests/ -v

# Test specific feature
pytest tests/test_pipeline.py -v
pytest tests/test_auth_otp_flow.py -s
```

### Manual Testing Endpoints

```bash
# 1. Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# 2. Verify OTP (use code from email)
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com", "otp":"123456"}'

# 3. Search for product (main endpoint)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_ID" \
  -d '{
    "product_name": "iPhone 14 Pro",
    "user_email": "test@example.com"
  }'

# 4. Get dashboard
curl -X GET http://localhost:8000/api/dashboard/YOUR_USER_ID \
  -H "Authorization: Bearer YOUR_USER_ID"

# 5. Get wishlist
curl -X GET http://localhost:8000/api/wishlist/YOUR_USER_ID \
  -H "Authorization: Bearer YOUR_USER_ID"
```

### Using API Docs (Swagger UI)
```
Open in browser: http://localhost:8000/docs
- Try out each endpoint
- See request/response schemas
- View all 19 endpoints
```

---

## 🐳 DOCKER & DEPLOYMENT

### Local Development
```bash
docker-compose up --build
# Starts: API (8000) + PostgreSQL (5432) + Redis (6379)
```

### Production Deployment
```bash
# Build image
docker build -t smartshop-ai:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e SUPABASE_URL=https://... \
  -e SUPABASE_KEY=... \
  -e COHERE_API_KEY=... \
  -e TAVILY_API_KEY=... \
  smartshop-ai:latest

# Scale to 3 instances
docker-compose up -d --scale api=3
```

### Health Checks
```bash
# API health
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "cache": "ready",
  "timestamp": "2026-05-18T15:30:00"
}
```

---

## 🎯 COMMON TASKS

### Add a New Endpoint
```python
# In main.py
@app.get("/api/my-endpoint/{item_id}")
async def my_endpoint(item_id: str, current_user: str = Depends(get_current_user)):
    """Description of what this endpoint does"""
    try:
        # Validate input
        is_valid, error = validate_user_id(item_id)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error)
        
        # Get data from DB
        result = supabase_db.table('items').select('*').eq('id', item_id).execute()
        
        # Return response
        return {"success": True, "data": result.data}
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch item")
```

### Add a New Agent
```python
# In agents/my_agent.py
def run_my_agent(state: dict) -> dict:
    """Agent description"""
    try:
        # Read from state
        product_name = state.get("product_name", "").strip()
        
        # Process
        result = do_something(product_name)
        
        # Return updated state
        return {
            "my_agent_output": result,
            "my_agent_status": "complete"
        }
    except Exception as e:
        app_logger.error(f"Agent error: {str(e)}")
        return {"error": str(e)}

# In graph/pipeline.py
from agents.my_agent import run_my_agent

graph.add_node("my_agent", run_my_agent)
# Add to execution order...
```

### Query Database
```python
# Simple select
result = supabase_db.table('products').select('*').limit(10).execute()
products = result.data  # List of dicts

# With filter
result = supabase_db.table('products')\
    .select('*')\
    .eq('brand', 'Apple')\
    .gt('average_rating', 4.0)\
    .execute()

# With order & limit
result = supabase_db.table('product_prices')\
    .select('*')\
    .order('last_checked', desc=True)\
    .limit(5)\
    .execute()

# Insert data
result = supabase_db.table('products').insert({
    "name": "iPhone 14 Pro",
    "brand": "Apple",
    "price": 79999
}).execute()
new_id = result.data[0]['id']

# Update data
result = supabase_db.table('products')\
    .update({"average_rating": 4.5})\
    .eq('id', product_id)\
    .execute()

# Delete data
result = supabase_db.table('products')\
    .delete()\
    .eq('id', product_id)\
    .execute()
```

---

## 🔍 DEBUGGING

### Check Logs
```bash
# Docker logs
docker-compose logs -f api

# View specific error
docker-compose logs api | grep "ERROR"

# View agent execution
docker-compose logs api | grep "Agent"
```

### Enable Debug Logging
```python
# In main.py or agents
import logging
logging.basicConfig(level=logging.DEBUG)
app_logger.debug("Debug message")
```

### Check Database Connection
```bash
# Connect to PostgreSQL
psql -U smartshop_user -h localhost -d smartshop_ai

# List tables
\dt

# Query data
SELECT * FROM products LIMIT 5;
```

### Check Redis Cache
```bash
# Connect to Redis
redis-cli

# List all keys
keys *

# Get specific key
get dashboard_user_id

# Clear cache
FLUSHDB
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Supabase not configured` | Missing env vars | Set `SUPABASE_URL`, `SUPABASE_KEY` |
| `'coroutine' object is not iterable` | Async decorator issue | See debugging.md in memory |
| `TAVILY_API_KEY not found` | Missing API key | Add to .env file |
| `OTP expired` | User took >10 min | Request new OTP |
| `Connection refused: localhost:6379` | Redis not running | Run `redis-server` or docker-compose |
| `CORS error on frontend` | ALLOWED_ORIGINS not set | Update main.py CORS config |

---

## 📚 FURTHER READING

| Document | Content |
|----------|---------|
| [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md) | Complete system architecture (this file) |
| [README.md](README.md) | Project overview & quick start |
| [QUICKSTART.md](QUICKSTART.md) | Setup instructions |
| [docs/DEPLOYMENT/DEPLOYMENT.md](docs/DEPLOYMENT/DEPLOYMENT.md) | Production deployment |
| [docs/DEVELOPMENT/DEVELOPER_GUIDE.md](docs/DEVELOPMENT/DEVELOPER_GUIDE.md) | Code architecture |
| [docs/DEVELOPMENT/API_DOCUMENTATION.md](docs/DEVELOPMENT/API_DOCUMENTATION.md) | All 19 endpoints |
| [docs/SETUP/OTP_SETUP.md](docs/SETUP/OTP_SETUP.md) | Email configuration |

---

## 💡 KEY DECISIONS & WHY

| Decision | Why? |
|----------|------|
| **5 Agents** | Modularity, reusability, easy upgrades |
| **LangGraph** | State management, visualization, monitoring |
| **Tavily Search** | No legal issues, real-time, CloudFlare bypass |
| **Cohere LLM** | Strong Indian market context, free tier |
| **Supabase** | PostgreSQL power, RLS security, migrations |
| **React Native** | Cross-platform (iOS/Android), native UX |
| **OTP Auth** | No passwords, better UX, lower security risk |
| **Dual-layer Cache** | Production-ready + dev fallback |

---

## 🚀 NEXT STEPS

1. **Read the full analysis:** [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md)
2. **Review the agents:** Check each agent's .py file in `/agents/`
3. **Explore the API:** Open http://localhost:8000/docs in browser
4. **Modify something:** Try adding a new endpoint or agent
5. **Deploy:** Use docker-compose for local testing

---

**Last Updated:** May 2026 | **Status:** Production Ready ✅
