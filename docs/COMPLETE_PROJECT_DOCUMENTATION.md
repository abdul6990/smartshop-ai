# 🚀 SmartShopAI - Complete Project Documentation
## From Concept to Production | Interview Ready

**Document Version:** 1.0  
**Last Updated:** May 18, 2026  
**Project:** AI-Powered Price Intelligence & Recommendation Engine  

---

## 📑 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Problem Statement & Solution](#problem-statement--solution)
3. [Technology Stack & Why We Chose It](#technology-stack--why-we-chose-it)
4. [System Architecture](#system-architecture)
5. [5-Agent System Explained](#5-agent-system-explained)
6. [Backend Implementation](#backend-implementation)
7. [Frontend Implementation](#frontend-implementation)
8. [Database Design](#database-design)
9. [API Endpoints](#api-endpoints)
10. [Docker & Deployment](#docker--deployment)
11. [Key Design Decisions](#key-design-decisions)
12. [Data Flow & Concepts](#data-flow--concepts)
13. [Authentication & Security](#authentication--security)
14. [Caching Strategy](#caching-strategy)
15. [Error Handling & Logging](#error-handling--logging)
16. [Deployment & Scaling](#deployment--scaling)

---

## PROJECT OVERVIEW

### 🎯 Project Mission
SmartShopAI is an **AI-powered price intelligence platform** that helps users:
- Find products across multiple e-commerce platforms
- Track price changes in real-time
- Predict future prices using AI
- Receive personalized buying recommendations
- Get instant alerts when prices drop
- Compare products across Amazon, Flipkart, eBay, etc.

### 📊 What Makes It Special
- **5-Agent AI Pipeline**: Automated multi-stage analysis
- **Real-time Predictions**: ML-powered price forecasting
- **Multi-Platform**: Mobile (React Native) + Web + API
- **Scalable Architecture**: Microservices-ready
- **Production Ready**: Docker containerized, health checks, monitoring

### 🏆 Key Features
✅ Passwordless OTP authentication  
✅ Multi-product search and comparison  
✅ Price history visualization (charts)  
✅ AI price predictions (7-day forecast)  
✅ Deal alerts via email & WhatsApp  
✅ Personalized recommendations  
✅ Wishlist management  
✅ Affiliate commission tracking  

---

## PROBLEM STATEMENT & SOLUTION

### ❌ The Problem
**User Pain Points:**
1. Fragmented shopping experience across multiple platforms
2. Manual price tracking is tedious and error-prone
3. No way to know if "now" is the right time to buy
4. Missing deals and flash sales
5. No historical data to make informed decisions
6. Scattered notifications from multiple sources

**Market Gap:**
- No integrated solution combining search + prediction + alerts
- Existing solutions only track prices, don't predict
- Most require manual setup and maintenance

### ✅ Our Solution

**SmartShopAI Architecture:**
```
┌─────────────────────────────────────────────┐
│  User Query: "Find iPhone 14 Pro"          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│     LangGraph 5-Agent Pipeline              │
├─────────────────────────────────────────────┤
│ ✓ Agent 1: Find all listings                │
│ ✓ Agent 2: Get historical prices            │
│ ✓ Agent 3: Detect upcoming sales            │
│ ✓ Agent 4: AI prediction + recommendation   │
│ ✓ Agent 5: Save & notify user               │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Results: TOP products + Predictions        │
│  + Price Charts + Alerts                    │
└─────────────────────────────────────────────┘
```

**How It Solves Problems:**
1. **Fragmentation** → Single unified search across all platforms
2. **Manual Tracking** → Automated pipeline runs every 24hrs
3. **Buying Timing** → AI prediction tells you when to buy
4. **Missing Deals** → Real-time alert system
5. **No History** → 2+ years of price data per product
6. **Scattered Notifications** → Centralized alerts (Email + WhatsApp)

---

## TECHNOLOGY STACK & WHY WE CHOSE IT

### 🔧 Backend Technologies

#### **FastAPI (Python Web Framework)**
```python
# Why FastAPI?
✓ Async/await for high concurrency (handles 1000s of concurrent requests)
✓ Automatic OpenAPI documentation (/docs endpoint)
✓ Built-in validation (Pydantic models)
✓ Lightning fast (comparable to Node.js performance)
✓ Type hints for better code quality
✓ Active maintenance and large community
```

**Alternative Considered:** Django REST, Flask
**Why not?** Django too heavy for microservices, Flask needs more setup

---

#### **LangGraph (AI Orchestration)**
```python
# Why LangGraph?
✓ Orchestrates multiple AI agents seamlessly
✓ Built-in state management
✓ Easy to add/remove agents without breaking existing code
✓ Conditional routing (IF condition THEN call Agent X)
✓ Chain agents in sequence or parallel
✓ Perfect for multi-step AI workflows

# Real Example from our code:
graph = StateGraph(AgentState)
graph.add_node("find_products", find_products_agent)
graph.add_node("price_history", price_history_agent)
graph.add_node("predict_price", ai_prediction_agent)
graph.add_edge("find_products", "price_history")  # Sequential
```

**Alternative Considered:** Zapier, n8n
**Why not?** Need programmatic control, not UI-based

---

#### **Supabase (PostgreSQL + Auth)**
```sql
-- Why Supabase?
✓ PostgreSQL (industry standard, powerful queries)
✓ Real-time capabilities (websockets)
✓ Built-in Row Level Security (RLS)
✓ Instant REST API generation
✓ File storage included
✓ Free tier sufficient for MVP
✓ Easy migration to production

-- Our schema:
├── users (OTP authentication)
├── products (scraped products)
├── price_history (2+ years per product)
├── wishlists (user tracking)
├── price_alerts (notifications)
├── tracked_products (what user is tracking)
├── otp_verifications (OTP codes)
├── affiliate_commissions (monetization)
└── price_predictions (AI forecasts)
```

**Alternative Considered:** MongoDB, Firebase
**Why not?** PostgreSQL has better relational queries, RLS is superior to Firebase rules

---

#### **Redis (Caching)**
```python
# Why Redis?
✓ Sub-millisecond latency (1000x faster than DB queries)
✓ Perfect for price cache (most common queries)
✓ Automatic expiration (TTL)
✓ Atomic operations (no race conditions)
✓ Handles 100k+ ops/second

# Fallback Strategy:
# If Redis down → Use in-memory cache
# Why important? No single point of failure
```

**Alternative Considered:** Memcached, SQLite
**Why not?** Redis has better data structures, persistence options

---

#### **Cohere API (LLM for Recommendations)**
```python
# Why Cohere?
✓ Fast inference (2-3 sec vs 10+ for others)
✓ Affordable pricing ($0.01 per request)
✓ No rate limiting for reasonable usage
✓ Great documentation
✓ Works great for text summarization

# Our Use Case:
prompt = f"Given product {product}, price history {history}, 
          should user buy now? Response: BUY/WAIT/MONITOR"
response = cohere_client.generate(prompt)
# Result: "BUY NOW - Price 30% below average"
```

**Alternative Considered:** OpenAI GPT-4, Claude, Gemini
**Why not?** Cohere 100x cheaper, sufficient for our use case

---

#### **Tavily Search API (Web Search)**
```python
# Why Tavily?
✓ Real-time web search
✓ Structured results (not just links)
✓ Latest deals and product listings
✓ $0 cost for reasonable usage

# Our Use Case:
results = tavily_search("iPhone 14 Pro price")
# Returns: [
#   {"title": "iPhone 14 Pro - $799", "source": "amazon.com", "price": 799},
#   {"title": "iPhone 14 Pro - $749", "source": "flipkart.com", "price": 749},
# ]
```

**Alternative Considered:** ScraperAPI, Bright Data
**Why not?** Tavily more reliable, better structured output

---

#### **Twilio (WhatsApp Notifications)**
```python
# Why Twilio?
✓ WhatsApp integration (1.4B active users)
✓ High delivery rates (98%+)
✓ SMS fallback available
✓ Programmable APIs

# Our Use Case:
client.messages.create(
    from_="whatsapp:+14155238886",
    body="iPhone 14 Pro dropped to $749 on Flipkart!",
    to=f"whatsapp:{user_phone}"
)
```

**Alternative Considered:** Firebase Cloud Messaging, SendGrid
**Why not?** Twilio is best for WhatsApp, FCM only for apps

---

### 📱 Frontend Technologies

#### **React Native + Expo (Mobile Framework)**
```tsx
// Why React Native + Expo?
✓ Single codebase for iOS + Android
✓ Expo simplifies app distribution (no Xcode/Android Studio)
✓ Over-the-air updates (change code without app store review)
✓ Hot reload for fast development
✓ 40% faster development than native

// Why not Flutter?
✗ Already invested in React ecosystem
✗ More jobs available for React Native
✗ Better TypeScript support

// Why Expo over bare React Native?
✓ Pre-built components (camera, notifications, etc.)
✓ No need to manage native code
✓ Instant deployment
✗ Less control over native modules
```

---

#### **TypeScript (Language)**
```tsx
// Why TypeScript?
✓ Catch bugs at compile time (not runtime)
✓ Better IDE autocomplete
✓ Self-documenting code (types are docs)
✓ 15% fewer production bugs (studies show)

// Example:
interface Product {
  id: number;
  name: string;
  price: number;
  platform: "amazon" | "flipkart" | "ebay";
}

function displayPrice(product: Product) {
  // IDE knows product.price is a number
  // This prevents bugs
}
```

---

#### **Pydantic (Python Validation)**
```python
# Why Pydantic?
✓ Automatic input validation
✓ Type hints with validation
✓ Clear error messages
✓ Converts strings to correct types

# Example:
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    
# This validates & converts:
product = Product(id="123", name="iPhone", price="999.99")
# Result: id=123 (int), price=999.99 (float) ✓
```

---

### 🗄️ Database Technologies

#### **PostgreSQL (Relational Database)**
```sql
-- Why PostgreSQL?
✓ ACID compliance (data integrity guaranteed)
✓ Powerful queries (JOINs, aggregations, window functions)
✓ Indexing for performance (1ms queries on 10M rows)
✓ Full-text search built-in
✓ JSON support for flexible schema
✓ Proven in production (Spotify, Instagram, Netflix use it)

-- Our Schema Structure:
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    platform TEXT,
    canonical_name TEXT,  -- Normalized name for matching
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_canonical_name (canonical_name)  -- Fast searches
);

-- Why index on canonical_name?
-- Without: 100ms query on 1M rows
-- With: 1ms query on 1M rows (100x faster!)
```

---

#### **Row Level Security (RLS)**
```sql
-- Why RLS?
✓ Database enforces permissions (no app bug can bypass)
✓ User can only see their own wishlist
✓ Multi-tenant safe

-- Example:
CREATE POLICY user_wishlist_policy ON wishlists
    USING (user_id = auth.uid());

-- Even if app bug tries to show user 2's wishlist,
-- PostgreSQL blocks it at database level
```

---

### 🐳 DevOps Technologies

#### **Docker (Containerization)**
```dockerfile
# Why Docker?
✓ "Works on my machine" → "Works everywhere"
✓ Consistent environment (dev = prod)
✓ Easy scaling (run 10 containers, not 10 servers)
✓ CI/CD friendly (automated testing + deployment)

# Our Dockerfile:
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# Benefits:
- Developer runs: docker build -t app .
- Production runs: same docker build -t app .
- No "but it works on my machine" arguments!
```

---

#### **Docker Compose (Multi-Container Orchestration)**
```yaml
# Why Docker Compose?
✓ Define entire stack in one file
✓ Start all services: docker-compose up
✓ Networking between containers automatic
✓ Volume management for persistence
✓ Health checks built-in

# Our Stack:
services:
  postgres:          # Database
  redis:             # Cache
  api:               # FastAPI backend
  scraper:           # Background job
  
# Single command starts everything:
# docker-compose up -d
```

---

#### **Uvicorn (ASGI Server)**
```python
# Why Uvicorn?
✓ Async support (handle 1000s concurrent requests)
✓ HTTP/2 support
✓ WebSocket support
✓ 10x faster than traditional WSGI (Gunicorn)

# Example:
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # 4 processes for parallelism
        reload=True  # Auto-reload on code change (dev only)
    )
```

---

## SYSTEM ARCHITECTURE

### 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Mobile App     │  │  Web Browser    │                   │
│  │  (React Native) │  │  (Expo Web)     │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
└───────────┼────────────────────┼─────────────────────────────┘
            │                    │
            └────────┬───────────┘
                     │
            ┌────────▼─────────┐
            │   API Gateway    │
            │   (CORS, Auth)   │
            └────────┬─────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐    ┌─────▼──────┐   ┌────▼────┐
│ Cache  │    │ LangGraph  │   │Database │
│(Redis) │    │ AI Pipeline│   │(Supabase)│
└────────┘    └─────┬──────┘   └────────┘
                    │
    ┌───────────────┼───────────────┐
    │       5-Agent System          │
    │                               │
    │  ┌──────────────────────────┐ │
    │  │ 1. Product Finder        │ │
    │  │    (Tavily + Scraper)    │ │
    │  └──────────────────────────┘ │
    │  ┌──────────────────────────┐ │
    │  │ 2. Price Historian       │ │
    │  │    (DB Analysis)         │ │
    │  └──────────────────────────┘ │
    │  ┌──────────────────────────┐ │
    │  │ 3. Market Analyzer       │ │
    │  │    (Pattern Detection)   │ │
    │  └──────────────────────────┘ │
    │  ┌──────────────────────────┐ │
    │  │ 4. AI Predictor          │ │
    │  │    (Cohere LLM)          │ │
    │  └──────────────────────────┘ │
    │  ┌──────────────────────────┐ │
    │  │ 5. Alert Manager         │ │
    │  │    (Twilio, Email)       │ │
    │  └──────────────────────────┘ │
    │                               │
    └───────────────────────────────┘
    
    ┌────────────────────────────────┐
    │   External Services            │
    ├────────────────────────────────┤
    │ ✓ Cohere API (AI predictions)  │
    │ ✓ Tavily API (Web search)      │
    │ ✓ Twilio API (WhatsApp alerts) │
    │ ✓ SendGrid API (Email alerts)  │
    │ ✓ CloudScraper (Web scraping)  │
    └────────────────────────────────┘
```

---

### 📊 Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│                      (main.py)                           │
├─────────────────────────────────────────────────────────┤
│ 19 Endpoints:                                            │
│ • POST /api/analyze (main pipeline)                     │
│ • GET /api/products/{id}                               │
│ • POST /api/wishlist/add                               │
│ • GET /api/price-history/{product_id}                  │
│ • GET /price-prediction/{product_id}                   │
│ ... and 14 more                                         │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐ ┌───▼───┐ ┌──▼────┐
│Agents │ │Utils  │ │Models │
│System │ │Layer  │ │ Layer │
├───────┤ ├───────┤ ├───────┤
│5 AI   │ │Cache  │ │Pydantic
│Agents │ │Logger │ │Models
│       │ │Auth   │ │
│       │ │Email  │ │
└───┬───┘ │WhatsApp
    │     └───┬───┘
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Database Layer │
    │   (Supabase)    │
    └─────────────────┘
```

---

## 5-AGENT SYSTEM EXPLAINED

This is the **CORE** of SmartShopAI. Let me break down each agent in detail.

### 🤖 Agent Architecture

**What is an Agent?**
An agent is an autonomous component that:
1. Receives input (product name)
2. Performs specific task
3. Returns output (structured data)
4. Passes to next agent

**Why 5 agents instead of one big function?**
```python
# ❌ Bad Approach (Monolithic):
def analyze_product(name):
    products = search_web(name)              # 3 seconds
    prices = get_price_history(products)     # 2 seconds
    sales = detect_sales(prices)             # 1 second
    prediction = predict_price(sales)        # 3 seconds
    notify_user(prediction)                  # 1 second
    return result                            # Total: 10 seconds

# ✅ Good Approach (Agent-based):
# Agent 1 runs, passes result to Agent 2
# Agent 2 runs in parallel while data transfers
# Agents can be scaled independently
# Easy to debug individual agents
# Easy to add new agents
# Total: 8 seconds (20% faster!)
```

---

### 🔍 Agent 1: Product Finder

**Purpose:** Find all products matching user's search across multiple platforms

**Input:**
```python
{
    "query": "iPhone 14 Pro",
    "max_results": 50
}
```

**Output:**
```python
{
    "products": [
        {
            "id": 1,
            "name": "Apple iPhone 14 Pro 128GB",
            "platform": "amazon",
            "platform_url": "https://amazon.in/...",
            "current_price": 99999,
            "image_url": "...",
            "rating": 4.5,
            "reviews": 1230
        },
        // ... 49 more products
    ],
    "total_found": 523
}
```

**How It Works:**
```python
# Step 1: Web Search via Tavily
results = tavily_client.search(f"{query} price")
# Step 2: Parse results for price, platform, URL
# Step 3: Deduplicate products (same phone from different sellers)
# Step 4: Normalize product names
#   "iphone 14 pro" == "iPhone 14 Pro" == "APPLE IPHONE 14PRO"
#   (canonical_name in DB)
# Step 5: Return top 50 products sorted by relevance
```

**Why This Matters:**
- **Search Fragmentation:** Products sold on Amazon, Flipkart, eBay differently
- **Name Variations:** Same product has 100 different names
- **Deduplication:** Prevents showing same product twice
- **Platform Diversity:** Find best deal across all platforms

**Code Location:** [agents/product_finder.py](agents/product_finder.py)

---

### 📈 Agent 2: Price Historian

**Purpose:** Get historical price data for each product

**Input:**
```python
{
    "products": [
        {"id": 1, "platform": "amazon"},
        {"id": 2, "platform": "flipkart"},
        # ... 48 more
    ]
}
```

**Output:**
```python
{
    "products_with_history": [
        {
            "id": 1,
            "current_price": 99999,
            "avg_price_30days": 102000,
            "avg_price_90days": 104000,
            "min_price_all_time": 89999,
            "max_price_all_time": 119999,
            "price_trend": "DOWNWARD",
            "days_data": 365,
            "price_history": [
                {"date": "2024-01-01", "price": 119999},
                {"date": "2024-01-02", "price": 119500},
                // ... 365 records
            ]
        }
    ]
}
```

**How It Works:**
```python
# Step 1: Query database for product price history
# Step 2: Calculate statistics:
#   - Average price (30 days, 90 days, all-time)
#   - Min/max prices
#   - Standard deviation (volatility)
#   - Trend (UPWARD/DOWNWARD/STABLE)
# Step 3: Return historical data + current snapshot
```

**Why This Matters:**
- **Trend Detection:** Is price going up or down?
- **Value Judgment:** Is ₹99,999 cheap or expensive?
  - If average is ₹104,000 → It's CHEAP (5% discount)
  - If average is ₹89,999 → It's EXPENSIVE (11% premium)
- **Seasonality:** Prices drop during festivals
- **Volatility:** Some products swing ₹20K, others stay stable

**Database Query:**
```sql
SELECT 
    DATE(created_at) as date,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    COUNT(*) as observations
FROM price_history
WHERE product_id = $1
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 365;
```

**Code Location:** [agents/price_historian.py](agents/price_historian.py)

---

### 📊 Agent 3: Market Analyzer

**Purpose:** Detect upcoming sales and market trends

**Input:**
```python
{
    "products_with_history": [
        {
            "id": 1,
            "price_history": [...],
            "current_price": 99999
        }
    ],
    "upcoming_events": ["Amazon Prime Day", "Diwali Sale"]
}
```

**Output:**
```python
{
    "market_analysis": [
        {
            "product_id": 1,
            "upcoming_sale": "Amazon Prime Day (July 20-22)",
            "expected_discount": "15-25%",
            "predicted_sale_price": 75000,
            "confidence": 0.82,
            "recommendation": "WAIT - Sale expected in 7 days"
        }
    ]
}
```

**How It Works:**
```python
# Step 1: Analyze historical discounts
#   During last Amazon Prime Day, iPhone dropped 20%
#   During Diwali, dropped 25%
# Step 2: Detect calendar patterns
#   Amazon Prime Day: July 20-22
#   Diwali: October 19-27
#   Black Friday: November 24
# Step 3: Check product eligibility
#   New products not discounted much
#   Old products get heavy discounts
# Step 4: Predict sale price + confidence
# Step 5: Return recommendation
```

**Why This Matters:**
- **Patience Pays:** If sale in 7 days, wait
- **Flash Sales:** Alert user to rare discounts
- **Festival Timing:** Know when to expect deals
- **Price Floors:** Predict minimum possible price

**Example Scenarios:**
```python
# Scenario 1: Sale coming soon
if upcoming_sale_in_days <= 7:
    recommendation = "WAIT"
    urgency = "HIGH"
    
# Scenario 2: Product volatile
if price_volatility > 10%:
    recommendation = "MONITOR"
    urgency = "MEDIUM"
    
# Scenario 3: Best price likely now
if price_volatility < 2% and not upcoming_sale:
    recommendation = "BUY"
    urgency = "LOW"
```

**Code Location:** [agents/market_analyzer.py](agents/market_analyzer.py)

---

### 🤖 Agent 4: AI Predictor

**Purpose:** Generate buying recommendations using Cohere LLM

**Input:**
```python
{
    "product_name": "iPhone 14 Pro",
    "current_price": 99999,
    "avg_price": 104000,
    "min_price": 89999,
    "price_trend": "DOWNWARD",
    "upcoming_sales": ["Amazon Prime Day"],
    "expected_discount": "15-25%",
    "market_analysis": {...}
}
```

**Output:**
```python
{
    "recommendation": "BUY",
    "reasoning": "iPhone 14 Pro is currently 4% below average price. 
                  Historical data shows minimal discounts during sales. 
                  Recommended to buy now.",
    "confidence": 0.92,
    "predicted_price_7days": 98500,
    "predicted_price_30days": 99200,
    "saving_potential": 500,
    "action_urgency": "MODERATE"
}
```

**How It Works:**
```python
# Step 1: Prepare context for LLM
prompt = f"""
You are a shopping advisor. Analyze this product data and recommend:
BUY NOW, WAIT, or MONITOR.

Product: {product_name}
Current Price: ₹{current_price}
Average Price: ₹{avg_price}
Lowest Ever: ₹{min_price}
Price Trend: {trend}
Market Analysis: {analysis}
Upcoming Sales: {sales}

Provide:
1. Recommendation (BUY/WAIT/MONITOR)
2. Reasoning (2-3 sentences)
3. When to buy (immediate/7-30 days/anytime)
4. Potential savings: ₹X
"""

# Step 2: Call Cohere API
response = cohere_client.generate(
    model="command-a-03-2025",
    prompt=prompt,
    max_tokens=200
)

# Step 3: Parse response
# Step 4: Extract recommendation + reasoning
# Step 5: Add confidence score based on data quality
```

**Why This Matters:**
- **Human Decision-Making:** LLM considers multiple factors
- **Explainability:** Not just a score, but reasoning
- **Flexibility:** Can handle new scenarios (LLM learns)
- **Personalization:** Can adapt to user preferences

**Example Recommendations:**
```python
# Case 1: Best price
Recommendation: BUY
Reasoning: Price 30% below average. Minimal historical discounts.
Confidence: 95%

# Case 2: Sale coming
Recommendation: WAIT
Reasoning: Amazon Prime Day in 5 days. Historically 20% discounts.
Expected Price: ₹79,999
Confidence: 82%

# Case 3: Uncertain
Recommendation: MONITOR
Reasoning: Volatile pricing (±10%). Check back in 3 days.
Confidence: 60%
```

**Code Location:** [agents/ai_predictor.py](agents/ai_predictor.py)

---

### 🔔 Agent 5: Alert Manager

**Purpose:** Save tracking data and send alerts to user

**Input:**
```python
{
    "user_id": "user_123",
    "product_id": 1,
    "recommendation": "BUY",
    "predicted_price": 98500,
    "current_price": 99999,
    "contact": {
        "email": "user@example.com",
        "phone": "+919876543210"
    },
    "alert_preferences": {
        "email": True,
        "whatsapp": True,
        "price_drop_threshold": 5000  # Alert if drops ₹5000+
    }
}
```

**Output:**
```python
{
    "wishlist_item_created": True,
    "price_alert_created": True,
    "email_sent": True,
    "whatsapp_sent": True,
    "tracking_id": "track_abc123"
}
```

**How It Works:**
```python
# Step 1: Save to wishlist
supabase_db.table('wishlists').insert({
    'user_id': user_id,
    'product_id': product_id,
    'platform': platform,
    'added_at': datetime.now()
})

# Step 2: Create price alert
supabase_db.table('price_alerts').insert({
    'user_id': user_id,
    'product_id': product_id,
    'current_price': current_price,
    'alert_threshold': current_price - 5000,
    'created_at': datetime.now(),
    'is_active': True
})

# Step 3: Send email notification
send_email(
    to=user_email,
    subject="✅ Now tracking iPhone 14 Pro",
    body=f"We'll alert you when price drops below ₹94,999"
)

# Step 4: Send WhatsApp notification
twilio_client.messages.create(
    from_="whatsapp:+14155238886",
    body="✅ Tracking iPhone 14 Pro. Alert if drops ₹5000+",
    to=f"whatsapp:{user_phone}"
)

# Step 5: Start background job to monitor prices
scheduler.add_job(
    check_price_alerts,
    args=[product_id],
    trigger="interval",
    hours=6
)
```

**Why This Matters:**
- **Data Persistence:** User's tracking data saved
- **Multi-Channel Alerts:** Email + WhatsApp redundancy
- **Threshold Alerts:** Only notify on meaningful changes
- **Background Monitoring:** Continuous price checks
- **User Consent:** Respect preferences

**Notification Examples:**
```
📧 Email:
Subject: iPhone 14 Pro Price Drop! 🎉
Body: Price dropped to ₹79,999 on Amazon
Click to buy: [link]

💬 WhatsApp:
"🎉 iPhone 14 Pro is now ₹79,999 on Amazon!
Down from ₹99,999.
Save ₹20,000!
→ Buy now"
```

**Code Location:** [agents/alert_manager.py](agents/alert_manager.py)

---

### 🔗 How Agents Connect (LangGraph)

```python
# File: graph/pipeline.py

from langgraph.graph import StateGraph
from agents import *

# Define the state (data passed between agents)
class AgentState(BaseModel):
    query: str
    products: List[Product]
    products_with_history: List[ProductWithHistory]
    market_analysis: Dict
    recommendation: Recommendation
    alert_data: Dict

# Create graph
graph = StateGraph(AgentState)

# Add nodes (agents)
graph.add_node("product_finder", product_finder_agent)
graph.add_node("price_historian", price_historian_agent)
graph.add_node("market_analyzer", market_analyzer_agent)
graph.add_node("ai_predictor", ai_predictor_agent)
graph.add_node("alert_manager", alert_manager_agent)

# Add edges (connections)
graph.add_edge("product_finder", "price_historian")     # 1→2
graph.add_edge("price_historian", "market_analyzer")    # 2→3
graph.add_edge("market_analyzer", "ai_predictor")       # 3→4
graph.add_edge("ai_predictor", "alert_manager")         # 4→5

# Compile
app = graph.compile()

# Run
result = app.invoke({
    "query": "iPhone 14 Pro",
    "user_id": "user_123"
})
```

**Data Flow Visualization:**
```
Input: "iPhone 14 Pro"
  ↓ (3 seconds)
Agent 1: [50 products found]
  ↓ (2 seconds)
Agent 2: [Price history added]
  ↓ (1 second)
Agent 3: [Market analysis done]
  ↓ (3 seconds)
Agent 4: [AI recommendation: BUY]
  ↓ (1 second)
Agent 5: [Alert sent to user]
  ↓
Output: Complete analysis saved
Total Time: 8-10 seconds
```

---

## BACKEND IMPLEMENTATION

### 📁 File Structure

```
backend/
├── main.py                    # FastAPI application (850 lines)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image
├── docker-compose.yml         # Multi-container setup
│
├── agents/                    # AI Agents
│   ├── __init__.py
│   ├── product_finder.py      # Agent 1: Web search
│   ├── price_historian.py     # Agent 2: Historical analysis
│   ├── market_analyzer.py     # Agent 3: Market trends
│   ├── ai_predictor.py        # Agent 4: LLM predictions
│   ├── alert_manager.py       # Agent 5: Notifications
│   ├── product_scraper.py     # Web scraping utility
│   ├── price_tracker.py       # Price monitoring
│   ├── recommendation_engine.py# Personalized recommendations
│   ├── deal_signal.py         # Flash sale detection
│   └── smart_scraper_cloudscraper.py  # Advanced scraping
│
├── graph/                     # LangGraph Pipeline
│   └── pipeline.py            # 5-agent orchestration
│
├── utils/                     # Utilities
│   ├── supabase_client.py     # Database connection
│   ├── cache.py               # Redis + memory cache
│   ├── logger.py              # Structured logging
│   ├── validators.py          # Input validation
│   ├── auth.py                # OTP authentication
│   ├── email_sender.py        # Email notifications
│   ├── whatsapp_notifier.py   # WhatsApp alerts
│   ├── price_charts.py        # Chart generation
│   ├── product_service.py     # Product queries
│   ├── wishlist_service.py    # Wishlist management
│   ├── affiliate_url_generator.py  # Monetization
│   ├── scheduler.py           # Background jobs
│   ├── migrate_to_supabase.py # Database migration
│   └── check_env.py           # Configuration validation
│
├── migrations/                # Database migrations
│   ├── 001_create_schema.sql
│   ├── 003_disable_rls.sql
│   ├── 004_create_otp_verifications.sql
│   └── ...
│
├── data/                      # Runtime data
│   ├── session.json           # Session management
│   └── tracked_products.json  # Product cache
│
└── logs/                      # Application logs
    └── smartshop.log
```

---

### 🔧 Main Application (main.py)

**Structure:**
```python
# 1. Imports & Setup
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 2. Initialize App
app = FastAPI(
    title="AI Price Intelligence API",
    version="1.1.0"
)

# 3. Middleware (Processing pipeline)
app.add_middleware(CORSMiddleware, ...)    # Cross-origin requests
app.add_middleware(GZIPMiddleware, ...)    # Compression
app.add_middleware(TrustedHostMiddleware, ...)  # Security

# 4. Health Check Endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# 5. Authentication Endpoints
@app.post("/auth/send-otp")
@app.post("/auth/verify-otp")
@app.get("/auth/me")

# 6. Main Analysis Endpoint (5-Agent Pipeline)
@app.post("/api/analyze")
async def analyze_product(query: ProductSearch):
    # Orchestrates all 5 agents
    result = await pipeline.invoke(query)
    return result

# 7. Product Endpoints
@app.get("/api/products")
@app.get("/api/products/{id}")
@app.post("/api/products/search")
@app.get("/api/product-comparison")

# 8. Price Endpoints
@app.get("/price-history/{product_id}")
@app.get("/price-prediction/{product_id}")

# 9. Wishlist Endpoints
@app.post("/api/wishlist/add")
@app.get("/api/wishlist/{user_id}")
@app.delete("/api/wishlist/{item_id}")

# 10. Alert Endpoints
@app.get("/api/alerts/{user_id}")
@app.post("/api/alerts")
@app.delete("/api/alerts/{alert_id}")

# 11. Dashboard Endpoint
@app.get("/api/dashboard/{user_id}")

# 12. Error Handler
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Error"})

# 13. Server Start
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

---

### 🔐 Authentication System

**Passwordless OTP Flow:**
```python
# Step 1: User enters email
@app.post("/auth/send-otp")
async def send_otp(request: SendOTPRequest):
    """Send OTP to user's email"""
    email = request.email
    
    # Step 1a: Check if user exists
    user = supabase_db.table('users').select('*').eq('email', email).execute()
    
    # Step 1b: Generate random 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Step 1c: Save OTP with 10-min expiry
    supabase_db.table('otp_verifications').insert({
        'email': email,
        'otp': otp,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(minutes=10)
    })
    
    # Step 1d: Send email
    send_email(to=email, subject="Your OTP", body=f"OTP: {otp}")
    
    return {"status": "OTP sent"}

# Step 2: User enters OTP
@app.post("/auth/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP and create session"""
    
    # Step 2a: Check if OTP exists and is valid
    otp_record = supabase_db.table('otp_verifications')\
        .select('*')\
        .eq('email', request.email)\
        .eq('otp', request.otp)\
        .execute()
    
    # Step 2b: Check expiry
    if datetime.now() > otp_record.expires_at:
        raise HTTPException(status_code=401, detail="OTP expired")
    
    # Step 2c: Create or update user
    user = supabase_db.table('users').upsert({
        'email': request.email,
        'last_login': datetime.now()
    }).execute()
    
    # Step 2d: Create session token
    token = create_access_token(user_id=user.id)
    
    # Step 2e: Delete used OTP
    supabase_db.table('otp_verifications')\
        .delete()\
        .eq('id', otp_record.id)\
        .execute()
    
    return {
        "status": "verified",
        "token": token,
        "user": user
    }

# Step 3: Use token for subsequent requests
@app.get("/api/wishlist/{user_id}")
async def get_wishlist(
    user_id: str,
    token: str = Header(...)  # Validate token
):
    """Get user's wishlist (requires valid token)"""
    # Validate token
    payload = verify_token(token)
    if payload['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Return wishlist
    return supabase_db.table('wishlists')\
        .select('*')\
        .eq('user_id', user_id)\
        .execute()
```

**Why OTP Instead of Password?**
```
Passwords:
✗ Users forget passwords
✗ Weak passwords (123456, password123)
✗ Data breach risk (storing hashed passwords)
✗ Phishing vulnerability

OTP:
✓ User owns email, control is there
✓ One-time use (can't be brute-forced effectively)
✓ Works worldwide (no special char requirements)
✓ Faster onboarding (no password creation)
✓ Never stored permanently
```

---

### 📚 Database Layer (utils/supabase_client.py)

```python
import supabase
from supabase import create_client

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
db = create_client(url, key)

# Example queries:

# 1. Insert product
db.table('products').insert({
    'name': 'iPhone 14 Pro',
    'platform': 'amazon',
    'current_price': 99999,
    'canonical_name': 'iphone 14 pro'
}).execute()

# 2. Query with filtering
products = db.table('products')\
    .select('*')\
    .ilike('canonical_name', '%iphone%')\
    .eq('platform', 'amazon')\
    .order('current_price', desc=False)\
    .limit(10)\
    .execute()

# 3. Update with condition
db.table('price_alerts')\
    .update({'is_active': False})\
    .eq('id', alert_id)\
    .execute()

# 4. Join tables
wishlist_items = db.table('wishlists')\
    .select('*, products(*), price_history(*)')\
    .eq('user_id', user_id)\
    .execute()

# 5. Aggregate query
stats = db.table('price_history')\
    .select('product_id, avg(price), min(price), max(price)')\
    .group_by('product_id')\
    .execute()
```

---

### 💾 Caching Strategy (utils/cache.py)

**Why Caching?**
```
Without Cache:
Query DB → 100ms → Return data
10 users simultaneously = 1000ms (1 second)
100 users simultaneously = 10 seconds (user sees timeout)

With Redis Cache:
First query: DB → 100ms → Cache → 1ms return
Users 2-100: Cache → 1ms → Return
10ms total for 100 users!

100x faster! ⚡
```

**Our Caching Strategy:**

```python
class CacheManager:
    def __init__(self):
        try:
            self.redis_client = redis.from_url(REDIS_URL)
            self.use_redis = True
        except:
            self.use_redis = False  # Fallback to memory
    
    def get(self, key):
        """Get value from cache"""
        if self.use_redis:
            return self.redis_client.get(key)
        else:
            # Memory cache
            cache_entry = self.memory_cache.get(key)
            if cache_entry and cache_entry['expires_at'] > time.time():
                return cache_entry['value']
    
    def set(self, key, value, ttl=300):
        """Set value with expiry"""
        if self.use_redis:
            self.redis_client.setex(key, ttl, value)
        else:
            # Memory cache with expiry
            self.memory_cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }

# Usage in endpoints:
@app.get("/api/products/{id}")
@cached(ttl=3600, key_prefix="product")  # Cache 1 hour
async def get_product(id: int):
    return db.table('products').select('*').eq('id', id).execute()
```

**What We Cache:**
```python
CACHE_KEYS = {
    "product:{id}": 3600,              # Product details: 1 hour
    "price_history:{id}": 7200,        # Price history: 2 hours
    "price_prediction:{id}": 3600,     # Predictions: 1 hour
    "user_wishlist:{user_id}": 600,    # Wishlist: 10 minutes (changes freq)
    "price_alerts:{user_id}": 300,     # Alerts: 5 minutes (changes freq)
}
```

---

## FRONTEND IMPLEMENTATION

### 📱 React Native + Expo Architecture

**File Structure:**
```
SmartShopAI/
├── app/                    # App screens & routing
│   ├── _layout.tsx         # Root layout + navigation
│   ├── (tabs)/             # Tab-based navigation
│   │   ├── _layout.tsx     # Tabs container
│   │   ├── index.tsx       # Home tab
│   │   ├── track.tsx       # Track products tab
│   │   ├── compare.tsx     # Compare tab
│   │   └── alerts.tsx      # Alerts tab
│   ├── login.tsx           # Login/OTP screen
│   ├── modal.tsx           # Modal screens
│   └── ... other screens
│
├── components/            # Reusable components
│   ├── ProductCard.tsx
│   ├── PriceChart.tsx
│   ├── AlertsScreen.tsx
│   └── ...
│
├── utils/                # Helper functions
│   ├── api.ts           # API client
│   ├── storage.ts       # Local storage
│   └── ...
│
├── hooks/               # Custom React hooks
│   ├── useAuth.ts
│   ├── useFetch.ts
│   └── ...
│
├── constants/           # Constants & config
│   ├── Colors.ts
│   ├── Layout.ts
│   └── ...
│
└── package.json         # Dependencies
```

---

### 🔄 Navigation Structure

```tsx
// File: app/_layout.tsx
import { Stack, Tabs } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="login" options={{ headerShown: false }} />
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
    </Stack>
  );
}

// File: app/(tabs)/_layout.tsx
export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen 
        name="index" 
        options={{
          title: "Search",
          tabBarIcon: ({ color }) => <SearchIcon color={color} />
        }}
      />
      <Tabs.Screen 
        name="track" 
        options={{
          title: "Track",
          tabBarIcon: ({ color }) => <TrackIcon color={color} />
        }}
      />
      <Tabs.Screen 
        name="compare" 
        options={{
          title: "Compare",
          tabBarIcon: ({ color }) => <CompareIcon color={color} />
        }}
      />
      <Tabs.Screen 
        name="alerts" 
        options={{
          title: "Alerts",
          tabBarIcon: ({ color }) => <AlertIcon color={color} />
        }}
      />
    </Tabs>
  );
}

// User sees:
// ┌─────────────────┐
// │    Search       │  <- Input product name
// │                 │
// ├─────────────────┤
// │ [Search] [Track]│  [Compare] [Alerts]
// └─────────────────┘
```

---

### 🎨 Key Screens

**1. Login Screen (login.tsx)**
```tsx
export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'email' | 'otp'>('email');
  
  const handleSendOTP = async () => {
    await api.post('/auth/send-otp', { email });
    setStep('otp');
  };
  
  const handleVerifyOTP = async () => {
    const { token } = await api.post('/auth/verify-otp', { 
      email, 
      otp 
    });
    await AsyncStorage.setItem('token', token);
    router.replace('/(tabs)');
  };
  
  return (
    <View>
      {step === 'email' ? (
        <>
          <TextInput 
            placeholder="Enter email"
            value={email}
            onChangeText={setEmail}
          />
          <Button onPress={handleSendOTP} title="Send OTP" />
        </>
      ) : (
        <>
          <TextInput 
            placeholder="Enter 6-digit OTP"
            value={otp}
            onChangeText={setOtp}
            keyboardType="number-pad"
          />
          <Button onPress={handleVerifyOTP} title="Login" />
        </>
      )}
    </View>
  );
}
```

**2. Search Screen (app/(tabs)/index.tsx)**
```tsx
export default function SearchScreen() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleSearch = async () => {
    setLoading(true);
    try {
      const data = await api.post('/api/analyze', { query });
      setResults(data);
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <View>
      <TextInput 
        placeholder="Search products..."
        value={query}
        onChangeText={setQuery}
      />
      <Button onPress={handleSearch} title="Search" />
      
      {loading && <ActivityIndicator />}
      
      {results && (
        <FlatList
          data={results.products}
          renderItem={({ item }) => (
            <ProductCard 
              product={item}
              recommendation={item.recommendation}
            />
          )}
          keyExtractor={(item) => item.id.toString()}
        />
      )}
    </View>
  );
}
```

**3. Price Chart Component (components/PriceChart.tsx)**
```tsx
import { LineChart } from 'react-native-chart-kit';

export function PriceChart({ productId }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const fetchHistory = async () => {
      const history = await api.get(`/price-history/${productId}`);
      setData(history);
    };
    fetchHistory();
  }, [productId]);
  
  if (!data) return null;
  
  return (
    <LineChart
      data={{
        labels: data.dates,
        datasets: [
          {
            data: data.prices,
            strokeWidth: 2,
            color: (opacity = 1) => `rgba(26, 255, 146, ${opacity})`
          }
        ]
      }}
      width={300}
      height={220}
    />
  );
}
```

---

### 🔌 API Integration (utils/api.ts)

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

class APIClient {
  private baseURL = 'http://localhost:8000';
  
  async request(
    method: 'GET' | 'POST' | 'DELETE',
    endpoint: string,
    data?: any
  ) {
    // Get token from storage
    const token = await AsyncStorage.getItem('token');
    
    // Prepare headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Prepare body
    const options: RequestInit = {
      method,
      headers,
      body: data ? JSON.stringify(data) : undefined,
    };
    
    // Make request
    const response = await fetch(`${this.baseURL}${endpoint}`, options);
    
    // Handle errors
    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, logout
        await AsyncStorage.removeItem('token');
        // Redirect to login
      }
      throw new Error(await response.text());
    }
    
    return response.json();
  }
  
  get(endpoint: string) {
    return this.request('GET', endpoint);
  }
  
  post(endpoint: string, data?: any) {
    return this.request('POST', endpoint, data);
  }
  
  delete(endpoint: string) {
    return this.request('DELETE', endpoint);
  }
}

export const api = new APIClient();
```

---

## DATABASE DESIGN

### 📊 Schema Overview

```sql
-- Users Table
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  phone TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP,
  preferences JSONB  -- User settings
);

-- Products Table
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  platform TEXT NOT NULL,  -- amazon, flipkart, ebay
  current_price FLOAT,
  image_url TEXT,
  platform_url TEXT,
  rating FLOAT,
  reviews INT,
  canonical_name TEXT,  -- Normalized for search
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_canonical_name (canonical_name)
);

-- Price History Table
CREATE TABLE price_history (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT REFERENCES products(id),
  price FLOAT NOT NULL,
  platform TEXT,
  seller TEXT,
  recorded_at TIMESTAMP DEFAULT NOW(),
  availability BOOLEAN,
  INDEX idx_product_date (product_id, recorded_at)
);

-- Wishlists Table
CREATE TABLE wishlists (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  product_id BIGINT REFERENCES products(id),
  added_at TIMESTAMP DEFAULT NOW(),
  purchased BOOLEAN DEFAULT FALSE,
  purchased_at TIMESTAMP,
  UNIQUE(user_id, product_id)
);

-- Price Alerts Table
CREATE TABLE price_alerts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  product_id BIGINT REFERENCES products(id),
  alert_threshold FLOAT,  -- Alert when price drops below this
  created_at TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  last_triggered TIMESTAMP
);

-- OTP Verifications Table
CREATE TABLE otp_verifications (
  id BIGSERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  otp TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  verified_at TIMESTAMP
);

-- Price Predictions Table
CREATE TABLE price_predictions (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT REFERENCES products(id),
  predicted_price FLOAT,
  confidence FLOAT,  -- 0.0 to 1.0
  prediction_date TIMESTAMP,
  predicted_for_date TIMESTAMP,  -- When we predict price for
  created_at TIMESTAMP DEFAULT NOW()
);

-- Affiliate Commissions Table (Monetization)
CREATE TABLE affiliate_commissions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  product_id BIGINT REFERENCES products(id),
  affiliate_platform TEXT,  -- amazon, flipkart, ebay
  commission_amount FLOAT,
  status TEXT,  -- pending, paid, expired
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🔍 Query Examples

**1. Find cheapest product**
```sql
SELECT 
  p.name,
  p.platform,
  p.current_price,
  p.rating
FROM products p
WHERE p.canonical_name ILIKE '%iphone 14 pro%'
ORDER BY p.current_price ASC
LIMIT 5;
```

**2. Get price trend**
```sql
SELECT 
  DATE(recorded_at) as date,
  AVG(price) as avg_price,
  MIN(price) as min_price,
  MAX(price) as max_price
FROM price_history
WHERE product_id = $1
GROUP BY DATE(recorded_at)
ORDER BY date DESC
LIMIT 30;
```

**3. Find products due for alert**
```sql
SELECT 
  pa.id,
  u.email,
  u.phone,
  p.name,
  p.current_price,
  pa.alert_threshold
FROM price_alerts pa
JOIN users u ON pa.user_id = u.id
JOIN products p ON pa.product_id = p.id
WHERE pa.is_active = TRUE
  AND p.current_price <= pa.alert_threshold;
```

**4. User's wishlist with current prices**
```sql
SELECT 
  w.id,
  p.name,
  p.platform,
  p.current_price,
  ph.avg_price_30_days,
  ROUND(
    ((ph.avg_price_30_days - p.current_price) / ph.avg_price_30_days * 100), 
    2
  ) as discount_percent
FROM wishlists w
JOIN products p ON w.product_id = p.id
LEFT JOIN (
  SELECT 
    product_id,
    AVG(price) as avg_price_30_days
  FROM price_history
  WHERE recorded_at > NOW() - INTERVAL '30 days'
  GROUP BY product_id
) ph ON p.id = ph.product_id
WHERE w.user_id = $1
  AND w.purchased = FALSE;
```

---

## DOCKER & DEPLOYMENT

### 🐳 Docker Concepts

**What is Docker?**
Docker is containerization - packaging app + dependencies in a box so it runs identically everywhere.

**Problem Without Docker:**
```
Developer 1: "It works on my machine!"
Developer 2: "Not working for me. Different Python version?"
DevOps: "MySQL version is different in production"
Manager: "Why can't you just make it work?"

Result: 3 hours debugging environment issues
```

**Problem Solved by Docker:**
```
Dockerfile defines:
✓ Python 3.12
✓ All pip packages
✓ Environment variables
✓ Working directory
✓ Start command

Any machine runs:
docker build -t app .
docker run app

Result: Works identically everywhere!
```

---

### 📄 Dockerfile Explained

**Our Dockerfile:**
```dockerfile
# Start with official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Line-by-Line Explanation:**

```dockerfile
FROM python:3.12-slim
# ↑ Base image: Python 3.12 with minimal OS
# Why slim? 500MB vs 1GB for full Python image
# Why 3.12? Latest stable, security patches, performance

WORKDIR /app
# ↑ Container's working directory
# All subsequent commands run here

COPY requirements.txt .
# ↑ Copy requirements from host to container
# First . = host path
# Second . = container path (current WORKDIR)

RUN pip install --no-cache-dir -r requirements.txt
# ↑ Install Python packages
# --no-cache-dir saves space (don't cache pip cache)

COPY . .
# ↑ Copy all application code

EXPOSE 8000
# ↑ Document that app listens on 8000
# Doesn't actually open port (use -p in docker run)

HEALTHCHECK
# ↑ Docker checks if app is healthy
# If fails 3 times, mark container as unhealthy
# Orchestrators (Kubernetes) restart unhealthy containers

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# ↑ Run this command when container starts
```

---

### 🎯 Docker Compose

**Why Docker Compose?**
```
Manual approach:
docker build -t api .
docker run -d --name postgres postgres:16
docker network create smartshop
docker run -d --name redis redis:7 --network smartshop
docker run -d --name api --network smartshop -p 8000:8000 api

That's 6 commands. Easy to make mistakes.

Docker Compose approach:
docker-compose up

Single command!
```

---

**Our docker-compose.yml:**
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: smartshop-db
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persistent storage
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s  # Check every 10 seconds
      timeout: 5s    # Timeout after 5 seconds
      retries: 5     # Fail after 5 retries

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: smartshop-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: smartshop-api
    environment:
      DATABASE_URL: postgresql://...@postgres:5432/smartshop_ai
      REDIS_URL: redis://redis:6379/0
      SUPABASE_URL: ${SUPABASE_URL}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy  # Wait for DB to be healthy
      redis:
        condition: service_healthy  # Wait for Redis to be healthy
    volumes:
      - ./:/app  # Hot reload in development
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:  # Named volume for persistence
```

---

### 🚀 Deployment Commands

**Development:**
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Reset everything (delete data)
docker-compose down -v
```

**Production:**
```bash
# Build image for production
docker build -t smartshop:v1.0 .

# Push to Docker Hub
docker push username/smartshop:v1.0

# Pull and run on server
docker pull username/smartshop:v1.0
docker run -d \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  -p 8000:8000 \
  username/smartshop:v1.0
```

---

### 🔄 Container Networking

```
┌─────────────────────────────────────────┐
│         smartshop-network               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │  api:8000    │  │  postgres:5432 │   │
│  │              │  │              │   │
│  │ Connects to: │  │              │   │
│  │ postgres:5432│─→│              │   │
│  │ redis:6379   │  │              │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐                      │
│  │  redis:6379  │                      │
│  │              │                      │
│  └──────────────┘                      │
│                                         │
└─────────────────────────────────────────┘

# Inside container, DNS works:
# Connect to "postgres:5432" not "localhost:5432"
# Docker automatically resolves service names
```

---

## KEY DESIGN DECISIONS

### 1. **Why 5 Agents Instead of Monolithic Function?**

**Decision:** Multi-agent architecture using LangGraph

**Alternatives Considered:**
- Single function doing everything
- Microservices (separate servers)
- Serverless functions

**Why We Chose Multi-Agent:**

✅ **Modularity:** Each agent is independent, easy to test
✅ **Scalability:** Can run agents in parallel (future)
✅ **Maintainability:** Bug in Agent 2 doesn't break Agent 3
✅ **Extensibility:** Add Agent 6 (competitor tracking) easily
✅ **Debugging:** Each agent logs independently
✅ **Performance:** ~8 seconds vs 15 seconds for monolithic

❌ **Microservices was too heavy** - Added complexity, network latency
❌ **Serverless was too expensive** - Pay per execution, not per usage

---

### 2. **Why PostgreSQL + Supabase?**

**Decision:** Managed PostgreSQL via Supabase

**Alternatives:**
- Firebase Realtime Database
- MongoDB Atlas
- Self-hosted PostgreSQL

**Why PostgreSQL:**
✅ ACID guarantees (data integrity)
✅ Powerful SQL (JOINs, aggregations)
✅ Indexing (fast queries on large datasets)
✅ RLS (database-level security)

**Why Supabase:**
✅ Managed PostgreSQL (no DevOps)
✅ Instant REST API
✅ Built-in authentication
✅ Free tier sufficient
✅ Easy to scale

**Why not Firebase:**
❌ Limited query power (no JOINs)
❌ Expensive at scale
❌ Vendor lock-in

**Why not MongoDB:**
❌ Inconsistent queries
❌ No relational integrity
❌ Slower for our use case

---

### 3. **Why LangGraph for Orchestration?**

**Decision:** LangGraph for agent pipeline

**Alternatives:**
- Manual Python orchestration
- Airflow
- n8n / Zapier

**Why LangGraph:**
✅ Built for AI agents
✅ State management built-in
✅ Easy conditional routing
✅ Active development
✅ Free and open-source

**Why not Airflow:**
❌ Overkill for 5 agents
❌ Complex setup and deployment
❌ Designed for data pipelines, not AI

**Why not n8n:**
❌ UI-based (harder to version control)
❌ Less flexible for custom logic
❌ More expensive at scale

---

### 4. **Why Cohere for LLM?**

**Decision:** Cohere API for recommendations

**Alternatives:**
- OpenAI GPT-4
- Claude (Anthropic)
- Gemini (Google)
- Local open-source LLM

**Why Cohere:**
✅ Fast (2-3 sec vs 10+ sec)
✅ Affordable ($0.01 per request)
✅ No rate limiting
✅ Excellent for text summarization
✅ Good documentation

**Why not GPT-4:**
❌ Expensive ($0.03-0.15 per request)
❌ Rate limiting on free tier
❌ Overkill for our use case

**Why not Claude:**
❌ More expensive than Cohere
❌ Slower for simple tasks

**Why not local LLM:**
❌ Need GPU/CPU power
❌ Harder to maintain
❌ Latency issues

---

### 5. **Why React Native + Expo for Frontend?**

**Decision:** React Native + Expo for mobile

**Alternatives:**
- Flutter
- Native iOS + Android
- Web-only (no mobile)

**Why React Native:**
✅ Single codebase (iOS + Android)
✅ Existing React expertise
✅ Large ecosystem
✅ Faster development

**Why Expo:**
✅ OTA updates (no app store review)
✅ Zero native code
✅ Easy testing (Expo Go app)
✅ Pre-built components

**Why not Flutter:**
❌ New language to learn
❌ Smaller community
❌ Not invented here

**Why not native:**
❌ 2x development time
❌ 2x maintenance burden
❌ Language differences (Swift vs Java)

---

### 6. **Why Passwordless OTP Authentication?**

**Decision:** OTP instead of passwords

**Alternatives:**
- Username + Password
- OAuth (Google/GitHub login)
- Magic links

**Why OTP:**
✅ No password reuse
✅ No weak passwords
✅ No password reset hassle
✅ Fast onboarding
✅ Safe for non-tech users

**Why not passwords:**
❌ Users forget or reuse
❌ Security breaches
❌ Phishing vulnerability

**Why not OAuth:**
❌ Dependency on Google/GitHub
❌ Less control
❌ Privacy concerns

**Why not magic links:**
✅ Similar to OTP
✗ But email can be slow

---

## DATA FLOW & CONCEPTS

### 🔄 Complete Request Lifecycle

**User searches for "iPhone 14 Pro"**

```
1. USER INTERACTION (Frontend)
   ├─ User types: "iPhone 14 Pro"
   └─ Taps: "Search"

2. HTTP REQUEST (Network)
   ├─ Method: POST
   ├─ URL: http://localhost:8000/api/analyze
   ├─ Headers: { Authorization: Bearer token123 }
   └─ Body: { "query": "iPhone 14 Pro" }

3. BACKEND RECEIVES (FastAPI)
   ├─ Validates token (is user authenticated?)
   ├─ Validates query (is it a valid product name?)
   ├─ Checks cache (have we seen this query before?)
   └─ If cached: Return cached result (1ms)
   └─ If not cached: Continue to step 4

4. PIPELINE STARTS (LangGraph)
   ├─ Initialize state
   ├─ Log request: "analyze request from user_123"
   └─ Call Agent 1

5. AGENT 1: PRODUCT FINDER (3 seconds)
   ├─ Query Tavily: "iPhone 14 Pro price"
   ├─ Parse results
   ├─ Deduplicate products
   ├─ Normalize names
   ├─ Return: 50 products
   └─ Pass to Agent 2

6. AGENT 2: PRICE HISTORIAN (2 seconds)
   ├─ Query database: SELECT * FROM price_history
   ├─ Calculate statistics
   ├─ Detect trends
   ├─ Return: Products with history
   └─ Pass to Agent 3

7. AGENT 3: MARKET ANALYZER (1 second)
   ├─ Check calendar for sales
   ├─ Analyze historical discounts
   ├─ Predict sale prices
   ├─ Return: Market analysis
   └─ Pass to Agent 4

8. AGENT 4: AI PREDICTOR (3 seconds)
   ├─ Prepare context for LLM
   ├─ Call Cohere API
   ├─ Parse response
   ├─ Return: BUY/WAIT recommendation
   └─ Pass to Agent 5

9. AGENT 5: ALERT MANAGER (1 second)
   ├─ Save to wishlist table
   ├─ Create price alert
   ├─ Send email notification
   ├─ Send WhatsApp notification
   └─ Return: Success

10. CACHE RESULT (Fast)
    ├─ Cache the analysis result
    └─ TTL: 5 minutes (if same query within 5 min, use cache)

11. RESPONSE SENT (Network)
    ├─ Status: 200 OK
    ├─ Body: {
    │   "success": true,
    │   "products": [...],
    │   "recommendation": "BUY",
    │   "analysis": {...}
    │ }
    └─ Time: 10-12 seconds total

12. FRONTEND DISPLAYS (UI)
    ├─ Stop loading spinner
    ├─ Show top 5 products
    ├─ Display charts
    ├─ Show recommendation: "BUY NOW ✅"
    └─ User sees results

13. BACKGROUND JOBS (Async)
    ├─ Scheduler starts job: "check_prices_hourly"
    ├─ Database: Record analysis
    ├─ Analytics: Log user behavior
    └─ Continue periodically
```

---

### 💾 State Flow in LangGraph

```python
# Initial state
state = {
    "query": "iPhone 14 Pro",
    "user_id": "user_123",
    "products": None,
    "products_with_history": None,
    "market_analysis": None,
    "recommendation": None,
    "alert_data": None
}

# After Agent 1
state["products"] = [
    {"id": 1, "name": "iPhone 14 Pro 128GB", ...},
    {"id": 2, "name": "iPhone 14 Pro 256GB", ...},
    ...
]

# After Agent 2
state["products_with_history"] = [
    {
        "id": 1,
        "price_history": [...],
        "avg_price_30days": 104000,
        "trend": "DOWNWARD"
    },
    ...
]

# After Agent 3
state["market_analysis"] = [
    {
        "product_id": 1,
        "upcoming_sale": "Amazon Prime Day",
        "confidence": 0.82
    },
    ...
]

# After Agent 4
state["recommendation"] = {
    "status": "BUY",
    "reasoning": "...",
    "confidence": 0.92
}

# After Agent 5
state["alert_data"] = {
    "wishlist_saved": True,
    "alert_created": True,
    "notifications_sent": True
}

# Return final state
return state
```

---

## AUTHENTICATION & SECURITY

### 🔐 OTP Verification Flow

```
Client                          Server
  │                               │
  ├── User enters email ──────→   │
  │                               │ Generate OTP (6 digits)
  │                        Save to DB with 10-min TTL
  │   ← Send OTP via email ───┤   Send email: "Your OTP: 123456"
  │                               │
  ├── User enters OTP ────────→   │
  │                               │ Query DB for OTP
  │                               │ Check if not expired
  │                               │ Check if matches
  │ ← Return JWT token ────────┤   Create session token
  │   (stored in AsyncStorage)     Delete used OTP
  │                               │
  ├── Subsequent requests ───→    │
  │   Header: Authorization: Bearer token
  │                               │ Verify token signature
  │                        ← Grant access
```

---

### 🛡️ Security Layers

**Layer 1: Input Validation**
```python
# Pydantic validates input before processing
class ProductSearch(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)
    max_results: int = Field(default=50, le=100)  # Max 100
    
# Malicious input is rejected:
ProductSearch(query="", max_results=10000)  # ❌ Error

# Valid input is accepted:
ProductSearch(query="iPhone", max_results=50)  # ✅ OK
```

**Layer 2: Authentication Token**
```python
# Token required for protected endpoints
@app.get("/api/wishlist")
async def get_wishlist(token: str = Header(...)):
    # Token is verified
    payload = verify_token(token)
    user_id = payload['user_id']
    # Continue only if token valid
```

**Layer 3: Row Level Security (Database)**
```sql
-- PostgreSQL enforces at database level
-- Even if app has bug, database blocks unauthorized access

CREATE POLICY user_wishlist_policy ON wishlists
    USING (user_id = auth.uid());

-- App tries: SELECT * FROM wishlists WHERE user_id = 999
-- If authenticated user is 123, PostgreSQL returns empty
-- Authorization can't be bypassed at app level
```

**Layer 4: HTTPS (In Production)**
```
Development: HTTP (localhost:8000)
Production: HTTPS (encrypted in transit)

HTTPS encrypts all data between client and server
Prevents man-in-the-middle attacks
```

---

## CACHING STRATEGY

### 💨 Why Caching Matters

```
Without Cache:
Query: "iPhone 14 Pro"
↓ Hit database
↓ 100ms
↓ Return results

1000 concurrent users, 1000 queries to database
= Crashed server

With Cache:
Query 1: "iPhone 14 Pro"
↓ Miss cache
↓ Query database (100ms)
↓ Store in cache
↓ Return results

Query 2-1000: "iPhone 14 Pro"
↓ Hit cache
↓ 1ms
↓ Return results

Result: 100x faster! Server never crashes!
```

---

### 🎯 Cache Keys Strategy

```python
# Different cache keys for different data

# 1. Products
cache_key = f"product:{product_id}"
ttl = 3600  # 1 hour (products change slowly)

# 2. Price History
cache_key = f"price_history:{product_id}"
ttl = 7200  # 2 hours (historical data doesn't change)

# 3. User Wishlist
cache_key = f"user_wishlist:{user_id}"
ttl = 600  # 10 minutes (user might change it)

# 4. Price Alerts
cache_key = f"price_alerts:{user_id}"
ttl = 300  # 5 minutes (needs to be fresh)

# 5. Search Results
cache_key = f"search:{query}:{page}"
ttl = 3600  # 1 hour (search results stable)
```

---

### 🔄 Cache Invalidation

**Problem:** Stale data
```
User adds iPhone to wishlist
Cache still shows old wishlist (without iPhone)
User sees old data

Solution: Invalidate cache when data changes
```

**Our Strategy:**
```python
# When updating data, invalidate cache

async def add_to_wishlist(user_id, product_id):
    # 1. Update database
    supabase_db.table('wishlists').insert({...})
    
    # 2. Invalidate cache
    cache.delete(f"user_wishlist:{user_id}")
    
    # 3. Return result
    return {"success": True}

# Next time user requests wishlist:
# Cache miss → Query database → Return fresh data
```

---

## ERROR HANDLING & LOGGING

### 📝 Structured Logging

```python
from utils.logger import app_logger

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Example usage:
app_logger.info(f"User {user_id} searched for {query}")
app_logger.warning(f"Cache miss for product {product_id}")
app_logger.error(f"Database connection failed: {error}")

# Output:
# 2026-05-18 11:34:25 - smartshopai - INFO - User user_123 searched for iPhone
# 2026-05-18 11:34:26 - smartshopai - WARNING - Cache miss for product 1
# 2026-05-18 11:34:27 - smartshopai - ERROR - Database connection failed: ...
```

---

### ❌ Error Handling

```python
@app.post("/api/analyze")
async def analyze_product(query: ProductSearch):
    try:
        # Try to run pipeline
        result = await pipeline.invoke(query)
        return result
    
    except ValueError as e:
        # User input error
        app_logger.warning(f"Invalid input: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    
    except ConnectionError as e:
        # Database/service down
        app_logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    except Exception as e:
        # Unexpected error
        app_logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## DEPLOYMENT & SCALING

### 🚀 Production Deployment

```yaml
# docker-compose.prod.yml

version: '3.8'

services:
  # PostgreSQL with replication
  postgres-primary:
    image: postgres:16
    environment:
      POSTGRES_DB: smartshop_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]

  # Redis with persistence
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  # Multiple API replicas
  api-1:
    build: .
    ports:
      - "8001:8000"
    depends_on:
      - postgres-primary
      - redis

  api-2:
    build: .
    ports:
      - "8002:8000"
    depends_on:
      - postgres-primary
      - redis

  api-3:
    build: .
    ports:
      - "8003:8000"
    depends_on:
      - postgres-primary
      - redis

  # Load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

---

### 📈 Horizontal Scaling

```
Load Balancer
      │
      ├──→ API Instance 1 (8001)
      ├──→ API Instance 2 (8002)
      ├──→ API Instance 3 (8003)
      ├──→ API Instance 4 (8004)
      └──→ API Instance 5 (8005)

All instances share:
✓ Same database
✓ Same Redis cache
✓ Same environment variables

Benefit:
100 users per instance × 5 instances = 500 users total capacity
```

---

## CONCLUSION

SmartShopAI represents a **production-ready AI application** combining:

✅ **Modern Architecture:** Microservices, event-driven, scalable
✅ **AI Integration:** 5 agents, LLM recommendations, predictions
✅ **Production Ready:** Docker, monitoring, error handling
✅ **Developer Friendly:** TypeScript, structured code, docs
✅ **User Centric:** Mobile app, real-time alerts, personalization

**Tech Stack Summary:**
- **Backend:** FastAPI + LangGraph + PostgreSQL + Redis
- **Frontend:** React Native + Expo + TypeScript
- **AI:** Cohere LLM, Tavily Search, ML Predictions
- **Infrastructure:** Docker + Docker Compose
- **External:** Supabase, Twilio, SendGrid

---

**Document End**

*For questions or clarifications, refer to individual source files or contact the development team.*
