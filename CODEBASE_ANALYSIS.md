# SmartShop AI - Complete Codebase Analysis

**Version:** 2.0.0 | **Date:** May 2026 | **Architecture:** 5-Agent LangGraph Pipeline  
**Frontend:** React Native (Expo) | **Backend:** FastAPI (Python 3.11) | **Database:** Supabase PostgreSQL

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

SmartShop AI is an **AI-powered price intelligence system** that helps Indian consumers find real deals on e-commerce platforms. The system orchestrates **5 specialized AI agents** through a **LangGraph pipeline** to analyze products, track prices, predict trends, and send alerts.

### High-Level Flow

```
User Search Query (Product Name + Email)
                ↓
         ┌─────────────────────────────────┐
         │   LANGGRAPH 5-AGENT PIPELINE    │
         └─────────────────────────────────┘
                ↓
    ┌───────────┬──────────────┬──────────────┬──────────────┬─────────────┐
    ↓           ↓              ↓              ↓              ↓             ↓
 Agent 1:   Agent 2:      Agent 3:       Agent 4:       Agent 5:
 Product   Price History Market        AI Predictor   Alert Manager
 Finder    & Deals       Analyzer       (Cohere)       (Notifications)
 (Tavily)  (Tavily)      (Tavily)
    ↓           ↓              ↓              ↓              ↓
 Products  Price Trends  Upcoming Sales  Buy/Wait Rec  Track & Notify
           & History     & Deals         + Timing
           
                        ↓
            JSON State → Supabase DB → Email/WhatsApp Alert
                        ↓
            Returns: TOP 5 PRODUCTS + PREDICTION
```

---

## 🤖 THE 5-AGENT SYSTEM

### **Agent 1: Product Finder**
**File:** [agents/product_finder.py](agents/product_finder.py)  
**Purpose:** Discover products across e-commerce platforms  
**Technology:** Tavily API + CloudScraper

**What it does:**
- Searches Tavily for product listings across Amazon, Flipkart, Meesho, Croma
- Extracts product name, price, rating from URLs using regex patterns
- Fetches real-time prices from product pages using CloudScraper
- Implements concurrent scraping with ThreadPoolExecutor for speed
- Returns ranked list of 5-100+ products with comprehensive scoring:
  - Price competitiveness (weighted)
  - Ratings normalization (0-5★)
  - Platform reputation (Amazon > Flipkart > Meesho)
  - Stock availability & seller verification

**Input:** Product name (e.g., "iPhone 14 Pro")  
**Output:** 
```json
{
  "products_found": [
    {
      "title": "Apple iPhone 14 Pro 128GB",
      "price": "₹79,999",
      "rating": "4.5★",
      "platform": "Amazon India",
      "url": "https://amazon.in/...",
      "score": 94.5,
      "badge": "Best Deal"
    }
  ],
  "total_found": 47,
  "best_5_products": [...]  // Top 5 by score
}
```

---

### **Agent 2: Price Historian**
**File:** [agents/price_historian.py](agents/price_historian.py)  
**Purpose:** Track historical prices and find deals  
**Technology:** Tavily API + Supabase

**What it does:**
- Searches Tavily for historical price trends (lowest prices ever)
- Identifies seasonal price patterns
- Finds current best prices across platforms
- Returns price history snippets for user context
- Stores price history in Supabase `product_prices` table

**Input:** Product name, best products from Agent 1  
**Output:**
```json
{
  "price_history": [
    {
      "title": "iPhone 14 Pro was ₹89,999 in December 2024",
      "snippet": "Historical lowest price...",
      "url": "..."
    }
  ],
  "best_price_data": [...]  // Current deals
}
```

---

### **Agent 3: Market Analyzer**
**File:** [agents/market_analyzer.py](agents/market_analyzer.py)  
**Purpose:** Identify upcoming sales and market trends  
**Technology:** Tavily API + Tavily Search

**What it does:**
- Searches for Amazon/Flipkart upcoming sales (Prime Day, Big Billion Days)
- Identifies product-specific deals and discounts
- Provides market trend context (seasonal peaks, clearance sales)
- Returns opportunities for better future prices

**Input:** Product name, current market data  
**Output:**
```json
{
  "upcoming_sales": [
    {
      "title": "Amazon Prime Day 2026 Expected Mid-June",
      "snippet": "Deals up to 40% off...",
      "url": "..."
    }
  ],
  "product_deals": [...]  // Specific product deals
}
```

---

### **Agent 4: AI Predictor**
**File:** [agents/ai_predictor.py](agents/ai_predictor.py)  
**Purpose:** Forecast prices and provide buying recommendations  
**Technology:** LangChain + Cohere LLM (command-r-plus-08-2024)

**What it does:**
- Aggregates all data from Agents 1-3
- Uses Cohere AI to analyze and synthesize findings
- Provides intelligent **BUY vs WAIT** recommendation
- Predicts 7-day price movement
- Suggests optimal buying time window
- Explains reasoning in natural language

**Cohere Prompt Structure:**
```
System: "You are an expert AI shopping analyst for Indian consumers in 2026"

Input: 
- Current products with prices & ratings
- Price history & historical lows
- Upcoming sales information
- Current product deals

Output:
1. CURRENT PRICE
2. HISTORICAL LOW
3. BUY OR WAIT (with confidence)
4. BEST TIME TO BUY
5. REASONING & ALTERNATIVES
```

**Example Output:**
```
The iPhone 14 Pro is currently ₹79,999 on Amazon India.
HISTORICAL LOW: ₹72,500 (Dec 2024)
RECOMMENDATION: WAIT (60% confidence)
BEST TIME: Prime Day (estimated early June 2026)
REASONING: Previous Amazon sales showed 10-15% discounts...
```

---

### **Agent 5: Alert Manager**
**File:** [agents/alert_manager.py](agents/alert_manager.py)  
**Purpose:** Save tracking data and orchestrate notifications  
**Technology:** JSON + Supabase + Email/WhatsApp APIs

**What it does:**
- Saves product to tracking list (data/tracked_products.json)
- Creates price alert records in Supabase
- Triggers email notifications to user
- Sends WhatsApp alerts for significant price drops (>₹1,000 or >10%)
- Logs user preferences for future recommendations

**Notification Flow:**
```
Price Drop Detected (current < threshold)
            ↓
Create Alert Record in Supabase
            ↓
Fetch User Preferences (email, whatsapp, phone)
            ↓
┌─────────────────────┬────────────────────┐
↓                     ↓                    ↓
Send Email        Send WhatsApp      Store in DB
(Gmail SMTP)      (Twilio API)       (for dashboard)
```

**Output to User:**
```
✅ 'iPhone 14 Pro' is now being tracked! (ID: 42)
Alert set for: ₹75,000 (20% below current)
You'll get email + WhatsApp alerts when price drops
```

---

## 🔄 DATA FLOW: REQUEST TO RESPONSE

### **Complete Request Lifecycle**

```
1. USER (Frontend App)
   POST /api/analyze
   {
     "product_name": "iPhone 14 Pro",
     "user_email": "user@example.com"
   }
   
   ↓
   
2. FASTAPI (main.py)
   - Validate email & product name
   - Log request
   - Cache check (optional)
   
   ↓
   
3. LANGGRAPH PIPELINE (graph/pipeline.py)
   Initial State:
   {
     "product_name": "iPhone 14 Pro",
     "user_email": "user@example.com",
     "products_found": [],
     "price_history": [],
     ...
   }
   
   ↓
   
4. AGENT NODES (Sequential Execution)
   
   Node 1: product_finder
   - Input: product_name
   - Output: products_found[], best_5_products[], total_found
   
   Node 2: price_historian  
   - Input: product_name, products_found
   - Output: price_history[], best_price_data[]
   
   Node 3: market_analyzer
   - Input: product_name, price_history
   - Output: upcoming_sales[], product_deals[]
   
   Node 4: ai_predictor
   - Input: ALL previous outputs
   - Output: ai_prediction (string with BUY/WAIT + reasoning)
   
   Node 5: alert_manager
   - Input: best_product, ai_prediction, user_email
   - Output: alert_status (tracking confirmation)
   
   ↓
   
5. DATABASE (Supabase)
   - Insert/Update: products table
   - Insert/Update: product_prices table (history)
   - Insert: price_alerts table
   - Insert: tracked_products (JSON fallback)
   
   ↓
   
6. NOTIFICATIONS (External APIs)
   - Email via Gmail SMTP
   - WhatsApp via Twilio
   - Store in Redis cache for real-time dashboard
   
   ↓
   
7. RESPONSE TO FRONTEND
   {
     "success": true,
     "product_name": "iPhone 14 Pro",
     "total_found": 47,
     "best_5_products": [
       {
         "title": "Apple iPhone 14 Pro 128GB",
         "price": "₹79,999",
         "rating": "4.5★",
         "platform": "Amazon India",
         "score": 94.5,
         "buy_url": "https://amazon.in/...",
         "affiliate_url": "https://affiliate.link/..." (optional)
       },
       ...
     ],
     "ai_prediction": "Recommendation: WAIT until Prime Day...",
     "alert_status": "✅ iPhone 14 Pro now being tracked!",
     "best_product": {...}
   }
   
   ↓
   
8. FRONTEND (React Native App)
   - Display TOP 5 products with cards
   - Show AI prediction in alert box
   - Display tracking confirmation
   - Update dashboard stats in real-time
```

---

## 📡 API ENDPOINTS (19 Total)

### **Authentication (2)**
- `POST /api/auth/request-otp` → Send OTP email to user
- `POST /api/auth/verify-otp` → Verify OTP, return session token

### **Product Analysis (2)**
- `POST /api/analyze` → **Main endpoint** - Run 5-agent pipeline, return TOP 5 products
- `GET /api/health` → Health check (DB, Redis, API status)

### **Price Tracking (3)**
- `GET /api/price-tracker/history/{product_id}` → Historical prices & trends
- `GET /api/price-tracker/recommendation` → Buy/wait recommendation
- `POST /api/price-tracker/track` → Record new price observation

### **Wishlist Management (5)**
- `GET /api/wishlist/{user_id}` → User's wishlist items
- `POST /api/wishlists` → Create new wishlist
- `POST /api/wishlists/{id}/items` → Add product to wishlist
- `DELETE /api/wishlists/{id}/items/{item_id}` → Remove from wishlist
- `GET /api/wishlists/{id}` → Get wishlist details

### **Price Alerts (3)**
- `GET /api/price-alerts` → User's active alerts
- `POST /api/price-alerts` → Create price threshold alert
- `DELETE /api/price-alerts/{id}` → Delete alert

### **Dashboard & Analytics (3)**
- `GET /api/dashboard/{user_id}` → Full user dashboard with stats
- `GET /api/deals` → Trending deals (products with recent price drops)
- `GET /api/charts/price` → Price history charts

### **Recommendations (1)**
- `GET /api/recommendations/personalized` → AI recommendations for user

---

## 🛠️ TECHNOLOGY STACK & RATIONALE

| Component | Technology | Version | Why? |
|-----------|-----------|---------|------|
| **Backend Framework** | FastAPI | 0.109.0 | Fast, async, auto-docs (Swagger), type-safe |
| **Server** | Uvicorn | 0.27.0 | ASGI server, production-ready |
| **Python** | CPython | 3.11 | Latest stable, good performance |
| **Async Runtime** | asyncio | Built-in | Native Python async/await support |
| **Database** | Supabase PostgreSQL | Latest | Managed, JSON support, real-time subscriptions |
| **Cache Layer** | Redis 7 | 7-alpine | Fast session cache, price history memoization |
| **Orchestration** | LangGraph | ≥1.0.0 | Multi-agent coordination, state management |
| **LLM** | Cohere API | command-r-plus-08-2024 | High-quality predictions, free tier availability |
| **Search** | Tavily API | ≥0.7.0 | Specialized for product search, real-time web |
| **Web Scraping** | CloudScraper | ≥1.2.71 | Bypass CloudFlare protection |
| **Notifications** | Gmail SMTP + Twilio | Latest | Free tier, reliable delivery |
| **Frontend** | React Native + Expo | 54.0.33 | Cross-platform (iOS/Android), native feel |
| **Navigation** | Expo Router | 6.0.23 | File-based routing, tab navigation |
| **Charts** | react-native-chart-kit | 6.12.0 | Beautiful price charts |
| **UI Components** | Expo Built-ins | Latest | Blur, LinearGradient, Vector icons |
| **Container** | Docker | Latest | Reproducible deployments, multi-service orchestration |
| **Orchestration** | docker-compose | 3.8 | Local dev + production setup |

---

## 📊 DATABASE SCHEMA (Supabase PostgreSQL)

### **Core Tables**

```sql
-- 1. USERS (Authentication)
users
├── id (UUID, PK)
├── email (VARCHAR 255, UNIQUE) ← Login identifier
├── phone (VARCHAR 20)
├── password_hash (SHA256)
├── first_name, last_name
├── profile_image_url
├── preferred_platforms (TEXT[]) ← User's favorite retailers
├── notification_enabled (BOOLEAN)
├── whatsapp_number (VARCHAR 20)
├── is_verified (BOOLEAN)
├── created_at, updated_at, last_login
└── INDEX: email

-- 2. CATEGORIES
categories
├── id (UUID, PK)
├── name (VARCHAR 100, UNIQUE) ← e.g., "Smartphones"
├── slug (VARCHAR 100, UNIQUE) ← URL-friendly name
├── description, icon_url
├── parent_category_id (FK) ← For hierarchical categories
└── Includes: Smartphones, Laptops, Tablets, Smart Watches, Headphones, Cameras, Smart Home, Gaming

-- 3. PLATFORMS (E-commerce retailers)
platforms
├── id (UUID, PK)
├── name (VARCHAR 100, UNIQUE) ← e.g., "Amazon India"
├── url (VARCHAR 255)
├── logo_url
├── commission_rate (DECIMAL 5.2) ← For affiliate calculations
├── is_active (BOOLEAN)
└── Pre-inserted: Amazon, Flipkart, Croma, Vijay Sales, Best Buy, eBay India

-- 4. PRODUCTS (Core product data)
products
├── id (UUID, PK)
├── name (VARCHAR 255)
├── brand (VARCHAR 100)
├── model, color, storage, ram
├── category_id (FK → categories)
├── description, image_url
├── additional_images (TEXT[])
├── average_rating (DECIMAL 3.2, 0-5)
├── total_reviews (INT)
├── unique_hash (VARCHAR 255, UNIQUE) ← Deduplication key
├── canonical_name (VARCHAR 255) ← Normalized for search
├── is_active, created_at, last_updated
└── INDEXes: name, brand, category, hash

-- 5. PRODUCT_PRICES (Price history & tracking)
product_prices
├── id (UUID, PK)
├── product_id (FK → products)
├── platform_id (FK → platforms)
├── price (DECIMAL 12.2) ← Current price
├── original_price (DECIMAL 12.2)
├── discount_percent (DECIMAL 5.2)
├── in_stock (BOOLEAN)
├── product_url (VARCHAR 500) ← Direct link to product
├── rating (DECIMAL 3.2) ← Platform-specific rating
├── reviews_count (INT)
├── last_checked (TIMESTAMP) ← When scraped
├── scrape_source (VARCHAR 100) ← 'amazon', 'flipkart', 'api', etc.
└── INDEXes: (product_id, platform_id), product_id, platform_id, date

-- 6. WISHLISTS (User's tracked products)
wishlists
├── id (UUID, PK)
├── user_id (FK → users)
├── name (VARCHAR 100) ← "My Wishlist" (default)
├── description (TEXT)
├── is_default (BOOLEAN)
├── is_public (BOOLEAN) ← Share with others
├── created_at, updated_at
└── INDEX: user_id

-- 7. WISHLIST_ITEMS (Products in wishlist)
wishlist_items
├── id (UUID, PK)
├── wishlist_id (FK → wishlists)
├── product_id (FK → products)
├── price_when_added (DECIMAL 12.2)
├── target_price (DECIMAL 12.2) ← Alert threshold
├── lowest_price_seen (DECIMAL 12.2)
├── current_best_price (DECIMAL 12.2)
├── current_best_platform (VARCHAR 100)
├── price_drop_count (INT) ← Times price dropped below target
├── is_purchased (BOOLEAN)
├── added_at, updated_at
└── INDEX: (wishlist_id, product_id)

-- 8. PRICE_ALERTS (Threshold-based alerts)
price_alerts
├── id (UUID, PK)
├── user_id (FK → users)
├── product_id (FK → products)
├── target_price (DECIMAL 12.2)
├── previous_price, new_price (DECIMAL 12.2)
├── price_drop_amount (DECIMAL 12.2)
├── price_drop_percent (DECIMAL 5.2)
├── platform_name (VARCHAR 100)
├── product_url (VARCHAR 500)
├── alert_triggered (BOOLEAN)
├── notification_sent (BOOLEAN)
├── created_at, triggered_at
└── INDEX: (user_id, created_at), product_id

-- 9. OTP_VERIFICATIONS (For passwordless login)
otp_verifications
├── id (UUID, PK)
├── email (VARCHAR 255)
├── otp_code (VARCHAR 6)
├── otp_expires_at (TIMESTAMP)
├── is_used (BOOLEAN)
├── created_at
└── INDEX: (email, created_at)
```

---

## 📱 FRONTEND STRUCTURE (React Native + Expo)

### **File Organization**

```
SmartShopAI/
├── app/
│   ├── _layout.tsx          # Root layout, navigation setup
│   ├── login.tsx            # OTP login screen
│   ├── index.tsx            # Home screen (search)
│   ├── track.tsx            # Price tracking screen
│   ├── compare.tsx          # Product comparison
│   ├── modal.tsx            # Modal dialogs
│   ├── (tabs)/              # Tab-based navigation
│   │   ├── home.tsx         # Tab: Home/Dashboard
│   │   ├── search.tsx       # Tab: Product search
│   │   ├── alerts.tsx       # Tab: Price alerts
│   │   └── profile.tsx      # Tab: User profile
│   
├── components/
│   ├── AlertsScreen.tsx     # Price alerts list component
│   ├── PriceTracker.tsx     # Real-time price updates
│   ├── RecommendationsList.tsx # AI recommendations
│   ├── price-chart.tsx      # Chart component (react-native-chart-kit)
│   ├── glass-components.tsx # Glassmorphism UI
│   ├── themed-text.tsx      # Typography system
│   ├── themed-view.tsx      # Reusable container
│   ├── ui/                  # Atomic UI components
│   └── external-link.tsx    # Link wrapper
│
├── hooks/
│   ├── useThemeColor.ts     # Theme colors (light/dark)
│   ├── useAuth.ts           # Authentication context
│   ├── useProducts.ts       # Product API calls
│   └── usePriceAlerts.ts    # Alert subscriptions
│
├── constants/
│   ├── Colors.ts            # Color palette (light/dark)
│   ├── Styles.ts            # Reusable styles
│   └── API.ts               # API endpoints config
│
├── utils/
│   ├── storage.ts           # AsyncStorage helpers
│   ├── formatting.ts        # Price, date formatting
│   ├── validators.ts        # Input validation
│   └── api-client.ts        # Fetch wrapper with auth
│
├── assets/
│   └── images/              # App images & icons
│
├── package.json             # Dependencies (React Native, Expo, etc.)
├── tsconfig.json            # TypeScript config
├── expo-env.d.ts            # Expo type definitions
└── app.json                 # Expo config (bundleIdentifier, etc.)
```

### **Key Components**

**AlertsScreen.tsx**
```tsx
// Displays list of active price alerts
// Subscribes to real-time Supabase updates
// Shows: Product, current price, target price, % savings
// Actions: Mark as purchased, delete alert, view product
```

**PriceTracker.tsx**
```tsx
// Real-time price updates for tracked products
// Uses React Native Chart Kit for price history visualization
// Shows: Price trend, historical high/low, recommendation
// Features: Haptic feedback on price drops, share buttons
```

**RecommendationsList.tsx**
```tsx
// AI-powered product recommendations
// Displays TOP 5 products from /api/analyze
// Shows: Scores, badges (Best Deal, Best Rating, etc.)
// Actions: Add to wishlist, view details, share
```

### **Navigation Structure**

```
Root (_layout.tsx)
├── Authentication Check
│   ├── NOT LOGGED IN → login.tsx (OTP flow)
│   └── LOGGED IN → Tab Navigation
│
Tab Navigation (Expo Router Tabs)
├── Tab 1: Home (Dashboard)
│   ├── Dashboard stats (items tracked, savings, deals)
│   ├── Recent activity timeline
│   └── Quick add product button
│
├── Tab 2: Search
│   ├── Search bar with voice input (expo-speech-recognition)
│   ├── Search results (TOP 5 products)
│   ├── Filter by: Platform, Price Range, Rating
│   └── Product detail modal
│
├── Tab 3: Alerts
│   ├── Active price alerts list
│   ├── Alert history
│   ├── Create new alert
│   └── Alert settings
│
└── Tab 4: Profile
    ├── User info
    ├── Preferences (platforms, notifications)
    ├── Logout button
    └── About/Help
```

### **Key Technologies**

- **Expo Router** - File-based routing (like Next.js)
- **@react-navigation** - Bottom tab navigation
- **AsyncStorage** - Local device storage for session/cache
- **Haptics** - Vibration feedback for user actions
- **Expo Blur** - Glassmorphism UI effects
- **Expo Vector Icons** - Material + Feather icons
- **React Native Chart Kit** - Price trend visualization
- **TypeScript** - Type-safe code

---

## 🔐 AUTHENTICATION FLOW (OTP-Based)

### **Passwordless Email OTP**

```
User Flow:
1. User enters email → POST /api/auth/request-otp
2. Backend:
   - Generate random 6-digit OTP
   - Save to OTP_VERIFICATIONS table + memory store
   - Set expiry: 10 minutes
   - Send email via Gmail SMTP
   
3. User receives email with OTP
4. User enters OTP → POST /api/auth/verify-otp
5. Backend:
   - Verify OTP is valid & not expired
   - Mark as used
   - Create/update user in users table
   - Generate session token
   - Return user_id to frontend
   
6. Frontend stores token in AsyncStorage
7. All subsequent requests include: Authorization: Bearer <user_id>
```

**Implementation Details** ([utils/auth.py](utils/auth.py))

```python
# OTP Storage Strategy:
# 1. In-Memory Store: Fast, for current session
# 2. Supabase Table: Persistent, for email verification
# 3. Dual Approach: Check memory first, fall back to DB

_OTP_MEMORY_STORE = {
    "user@example.com": {
        "otp": "123456",
        "otp_expires_at": "2026-05-18T15:30:00Z"
    }
}

# Generate 6-digit OTP
otp = ''.join(random.choices(string.digits, k=6))

# Verify flow:
1. Load OTP from memory (fast path)
2. If not found, query Supabase otp_verifications table
3. Check expiry: now < expires_at
4. Mark as used (prevent replay attacks)
5. Return session token
```

---

## 🔄 PIPELINE EXECUTION (LangGraph)

**File:** [graph/pipeline.py](graph/pipeline.py)

### **State Definition** (TypedDict)

```python
class PriceAgentState(TypedDict):
    # User Inputs
    product_name: str
    user_email: str
    
    # Agent 1 Outputs (Product Finder)
    products_found: list
    best_5_products: list
    all_products: list
    alternatives_found: list
    search_query: str
    total_found: int
    
    # Agent 2 Outputs (Price Historian)
    price_history: list
    best_price_data: list
    
    # Agent 3 Outputs (Market Analyzer)
    upcoming_sales: list
    product_deals: list
    
    # Agent 4 Outputs (AI Predictor)
    ai_prediction: str
    
    # Agent 5 Outputs (Alert Manager)
    alert_status: str
```

### **Graph Structure**

```
StateGraph(PriceAgentState)
    ↓
Add Nodes:
  - product_finder → run_product_finder()
  - price_historian → run_price_historian()
  - market_analyzer → run_market_analyzer()
  - ai_predictor → run_ai_predictor()
  - alert_manager → run_alert_manager()
    ↓
Set Entry: "product_finder"
    ↓
Add Sequential Edges:
  - product_finder → price_historian
  - price_historian → market_analyzer
  - market_analyzer → ai_predictor
  - ai_predictor → alert_manager
  - alert_manager → END
    ↓
Compile Graph
    ↓
Execute: pipeline.invoke({...state...})
    ↓
Returns: Final state dict with all agent outputs
```

### **Execution**

```python
def run_price_pipeline(product_name: str, user_email: str) -> dict:
    pipeline = build_pipeline()
    
    result = pipeline.invoke({
        "product_name": "iPhone 14 Pro",
        "user_email": "user@example.com",
        "products_found": [],
        "price_history": [],
        # ... all state fields initialized
    })
    
    # Returns completed state with all agent outputs
    return result
```

---

## 💾 CACHING STRATEGY

**File:** [utils/cache.py](utils/cache.py)

### **Dual-Layer Cache**

```
┌─────────────────────────────────┐
│    Request → Check Cache        │
├─────────────────────────────────┤
│                                 │
│   Layer 1: Redis (if available) │ ← Production cache
│   - Shared across instances      │
│   - TTL-based expiry            │
│   - Fast (in-memory)            │
│                                 │
│   Layer 2: In-Memory Dict       │ ← Development fallback
│   - Local process               │
│   - Custom expiry tracking      │
│   - No external dependency      │
│                                 │
└─────────────────────────────────┘
         ↓
    Cache HIT → Return cached value
         ↓
    Cache MISS → Execute logic → Store in cache → Return
```

### **Cached Endpoints**

```python
@cached(ttl=120, key_prefix="dashboard")
async def get_dashboard(user_id: str):
    # Cache user dashboard for 2 minutes
    # Key: dashboard_{user_id}

@cached(ttl=300, key_prefix="deals")
async def get_trending_deals():
    # Cache deals list for 5 minutes
    # Key: deals_all

@cached(ttl=600, key_prefix="recommendations")
async def get_recommendations(user_id: str):
    # Cache recommendations for 10 minutes
    # Key: recommendations_{user_id}
```

### **Cache Invalidation**

```python
# Automatic on update:
- Create wishlist → invalidate user's dashboard cache
- Add price alert → invalidate deals cache
- New product → invalidate search cache

# Manual cleanup:
cache_invalidate(key_prefix="dashboard")  # Clear all dashboard caches
cache.clear()  # Clear entire cache (Redis or memory)
```

---

## 🌍 DEPLOYMENT ARCHITECTURE

### **Docker Compose Setup** ([docker-compose.yml](docker-compose.yml))

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    env:
      POSTGRES_DB: smartshop_ai
      POSTGRES_USER: smartshop_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: 5432:5432
    volumes: postgres_data:/var/lib/postgresql/data
    healthcheck: pg_isready -U smartshop_user
  
  # Redis Cache
  redis:
    image: redis:7-alpine
    ports: 6379:6379
    healthcheck: redis-cli ping
  
  # FastAPI Backend
  api:
    build: .
    environment:
      DATABASE_URL: postgresql://smartshop_user:${POSTGRES_PASSWORD}@postgres:5432/smartshop_ai
      REDIS_URL: redis://redis:6379/0
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_KEY: ${SUPABASE_KEY}
      COHERE_API_KEY: ${COHERE_API_KEY}
      TAVILY_API_KEY: ${TAVILY_API_KEY}
      ALLOWED_ORIGINS: http://localhost:3000,http://localhost:8081
    ports: 8000:8000
    depends_on:
      postgres: condition: service_healthy
      redis: condition: service_healthy

volumes:
  postgres_data:
```

### **Dockerfile** ([Dockerfile](Dockerfile))

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Deployment Commands**

```bash
# Local Development
docker-compose up --build

# Production
docker-compose -f docker-compose.yml up -d --build

# Test API
curl http://localhost:8000/api/health
curl http://localhost:8000/docs  # Swagger UI

# View logs
docker-compose logs -f api

# Scale API
docker-compose up -d --scale api=3
```

---

## ⚙️ CONFIGURATION & ENVIRONMENT

### **Required .env Variables**

```bash
# Database
POSTGRES_DB=smartshop_ai
POSTGRES_USER=smartshop_user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://user:password@localhost:5432/smartshop_ai

# Cache
REDIS_URL=redis://localhost:6379/0

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# LLM & Search
COHERE_API_KEY=your-cohere-api-key
COHERE_MODEL_NAME=command-r-plus-08-2024
TAVILY_API_KEY=your-tavily-api-key

# Notifications
EMAIL_ADDRESS=your-gmail@gmail.com
EMAIL_PASSWORD=your-app-password  # Gmail App Passwords
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081,http://127.0.0.1:8081

# FastAPI
PORT=8000
DEBUG=False

# Logging
LOG_LEVEL=INFO
```

### **Runtime Configuration**

```python
# FastAPI CORS setup
allowed_origins = [
    "http://localhost:3000",        # Web frontend
    "http://localhost:8081",        # React Native (Expo)
    "http://127.0.0.1:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP compression for large responses
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 📊 UTILITY MODULES

### **[utils/supabase_client.py](utils/supabase_client.py)**
```python
# Singleton database connection
db = SupabaseDB()  # Auto-initializes from env

# Usage:
db.table('products').select('*').eq('id', product_id).execute()
db.is_connected  # Check connection status
db.health_check()  # Quick connectivity test
```

### **[utils/product_service.py](utils/product_service.py)**
```python
# Product deduplication & search
generate_product_hash(name, brand, model, color)  # MD5 hash
generate_canonical_name(name, brand)  # Normalized name
get_or_create_product(ProductCreate)  # Insert or retrieve
search_products(query, limit)  # Multi-platform search
get_product_with_prices(product_id)  # Full product details
```

### **[utils/wishlist_service.py](utils/wishlist_service.py)**
```python
# Wishlist management
get_user_wishlists(user_id)  # All user wishlists
get_wishlist_with_items(wishlist_id, user_id)  # Items + prices
add_to_wishlist(wishlist_id, product_id, target_price)  # Add item
remove_from_wishlist(wishlist_id, item_id)  # Remove item
get_price_alerts(user_id, limit=50)  # Active alerts
```

### **[utils/auth.py](utils/auth.py)**
```python
# OTP-based authentication
generate_otp()  # Random 6-digit code
request_otp(email)  # Send OTP email + store
verify_otp(email, otp)  # Validate & create session
_ensure_user_exists(db, email)  # Auto-create user
```

### **[utils/cache.py](utils/cache.py)**
```python
# Dual-layer cache (Redis + Memory)
cache.set(key, value, ttl=300)  # Store with expiry
cache.get(key)  # Retrieve cached value
cache.delete(key)  # Delete single entry
cache.clear()  # Clear all cache

@cached(ttl=120, key_prefix="dashboard")  # Decorator
async def get_dashboard(user_id):
    ...
```

### **[utils/logger.py](utils/logger.py)**
```python
# Structured logging
app_logger.info(msg)  # Info level
app_logger.warning(msg)  # Warning level
app_logger.error(msg, exc_info=True)  # Error with traceback
app_logger.debug(msg)  # Debug level
```

### **[utils/validators.py](utils/validators.py)**
```python
validate_email(email)  # Returns (is_valid, error_msg)
validate_product_name(name)  # 2-200 char check
validate_otp(otp)  # 6-digit check
validate_user_id(user_id)  # Min 5 chars
```

### **[utils/affiliate_url_generator.py](utils/affiliate_url_generator.py)**
```python
# Affiliate link generation (optional monetization)
build_purchase_links(product_url, platform_hint)
# Returns: { 'buy_url': direct_link, 'affiliate_url': affiliate_link }
```

### **[utils/whatsapp_notifier.py](utils/whatsapp_notifier.py)**
```python
# WhatsApp notifications via Twilio
whatsapp_notifier.send(phone_number, message)  # Send alert
# Message: "iPhone 14 Pro price dropped! ₹79,999 → ₹75,500 (5% off)"
```

### **[utils/email_sender.py](utils/email_sender.py)**
```python
# Email notifications via Gmail SMTP
send_otp_email(email, otp)  # Send OTP
send_price_alert_email(user_email, product, deal)  # Send deal
send_recommendation_email(user_email, products)  # Send recommendations
```

### **[utils/price_charts.py](utils/price_charts.py)**
```python
# Price history visualization
PriceChartManager.generate_chart(product_id, days=30)
# Returns: Chart data for react-native-chart-kit
```

---

## 🧪 TESTING SUITE

**Files in [tests/](tests/)**

```
test_affiliate_url_generator.py   # Affiliate URL generation
test_auth_otp_flow.py             # OTP authentication flow
test_buy_links.py                 # Direct/affiliate links
test_deal_signal.py               # Deal detection algorithm
test_pipeline.py                  # End-to-end agent pipeline
test_price_tracker.py             # Price tracking logic
test_recommendation_engine.py      # Recommendations
```

**Run Tests:**
```bash
pytest tests/
pytest tests/test_pipeline.py -v  # Verbose output
pytest tests/test_auth_otp_flow.py -s  # Show prints
```

---

## 🔗 KEY DESIGN DECISIONS

### **1. 5-Agent Pipeline (vs Monolithic)**
- ✅ Each agent focuses on one task (separation of concerns)
- ✅ Easy to replace/upgrade individual agents
- ✅ Parallel research capability (could run agents 1-3 in parallel)
- ✅ Clear data flow for debugging

### **2. LangGraph Orchestration (vs Direct Calls)**
- ✅ Built-in state management across agents
- ✅ Visualization of execution flow
- ✅ Easy to add conditional branching later
- ✅ Monitoring/logging built-in

### **3. Tavily API (vs Custom Web Scraping)**
- ✅ No legal issues (TOS compliant)
- ✅ Real-time web search results
- ✅ Handles CloudFlare/bot detection
- ✅ Cost-effective (free tier available)

### **4. Cohere LLM (vs GPT-4/Claude)**
- ✅ Strong performance on structured analysis
- ✅ Generous free tier (100k tokens/month)
- ✅ Good for Indian market context
- ✅ Faster response times

### **5. Supabase (vs Firebase)**
- ✅ PostgreSQL (more powerful queries than Firestore)
- ✅ Row-level security (RLS) for multi-tenancy
- ✅ Real-time subscriptions built-in
- ✅ Migrations support (version control for schema)

### **6. Dual-Layer Cache (Redis + Memory)**
- ✅ Production-ready when Redis available
- ✅ Graceful fallback for development
- ✅ Configurable TTL per endpoint
- ✅ Reduces API calls to external services

### **7. React Native (vs Web-only)**
- ✅ Cross-platform (iOS + Android)
- ✅ Native performance & UX
- ✅ Offline-first capability (AsyncStorage)
- ✅ Push notifications possible

### **8. Passwordless OTP (vs Traditional Login)**
- ✅ No password management burden
- ✅ Lower security risks (no password breaches)
- ✅ Better mobile UX
- ✅ Easier onboarding

---

## 🚀 DEPLOYMENT READY FEATURES

✅ **Docker containerization** for easy deployment  
✅ **CORS configured** for multi-origin requests  
✅ **Health checks** (API + Database)  
✅ **Graceful error handling** with proper HTTP status codes  
✅ **Request validation** using Pydantic  
✅ **Structured logging** for debugging  
✅ **Rate limiting ready** (can add middleware)  
✅ **Database migrations** versioned  
✅ **Async/await** for high concurrency  
✅ **Caching strategy** implemented  

---

## 📈 SYSTEM FLOW VISUALIZATION

```
DAILY USER JOURNEY
───────────────────

User Opens App
    ↓
[Not Logged In?]
    ├─→ Request OTP → Verify Email → Create Account
    │
[Logged In]
    ↓
[Dashboard]
    - Display: Total tracked items, savings, recent drops
    - Show: Top 3 active price alerts
    
[Search Tab]
    ├─→ Enter: "iPhone 14 Pro"
    ├─→ POST /api/analyze
    ├─→ Run 5-Agent Pipeline (8-15 seconds)
    │   ├─→ Agent 1: Find products (Tavily) 
    │   ├─→ Agent 2: Price history (Tavily)
    │   ├─→ Agent 3: Market analysis (Tavily)
    │   ├─→ Agent 4: AI prediction (Cohere)
    │   └─→ Agent 5: Save to tracking (DB)
    │
    └─→ Display TOP 5 Products:
        ├─ Product Card (Image, Price, Rating, Badge)
        ├─ AI Recommendation (BUY/WAIT + Reason)
        ├─ Actions: Add to wishlist, View on platform
        └─ Best product highlighted
    
[Wishlist Tab]
    - Display: Tracked items with current prices
    - Show: Savings vs price_when_added
    - Allow: Set target price, mark purchased
    
[Alerts Tab]
    - Real-time price drops
    - Swipe to mark done
    - Tap to view product
    
[Background]
    - Every hour: Check prices for all tracked items
    - If price < target: Send email + WhatsApp alert
    - Update dashboard stats
```

---

## 💡 KEY INSIGHTS

1. **State-Driven Architecture**: LangGraph manages state beautifully - each agent reads & writes to state dict
2. **Async-First**: FastAPI + Uvicorn handles 1000s of concurrent requests
3. **Data Deduplication**: unique_hash prevents duplicate products in DB
4. **Real-time UX**: React Native + Expo provides native mobile experience
5. **Flexible Scaling**: Can horizontal scale FastAPI instances behind load balancer
6. **Cost Effective**: All APIs on free tier (Cohere 100k tokens, Tavily 10 searches, Supabase 500MB)
7. **Privacy First**: OTP-based auth, no passwords stored, uses Supabase RLS for data isolation

---

## 🔍 QUICK REFERENCE

| Need | File | Function |
|------|------|----------|
| Run pipeline | [graph/pipeline.py](graph/pipeline.py) | `run_price_pipeline(name, email)` |
| Search products | [agents/product_finder.py](agents/product_finder.py) | `run_product_finder(state)` |
| Get user data | [utils/wishlist_service.py](utils/wishlist_service.py) | `get_user_wishlists(user_id)` |
| Database queries | [utils/supabase_client.py](utils/supabase_client.py) | `db.table(...).select(...)` |
| Cache values | [utils/cache.py](utils/cache.py) | `@cached(ttl=300)` |
| Auth flow | [utils/auth.py](utils/auth.py) | `request_otp()`, `verify_otp()` |
| API endpoints | [main.py](main.py) | `@app.post()`, `@app.get()` |
| Frontend UI | [SmartShopAI/components/](SmartShopAI/components/) | React Native components |
| Database schema | [migrations/001_create_schema.sql](migrations/001_create_schema.sql) | SQL DDL |

---

## 📞 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| API won't start | Check `SUPABASE_URL`, `SUPABASE_KEY` in .env |
| Pipeline returns empty | Verify `TAVILY_API_KEY` is set |
| No price predictions | Check `COHERE_API_KEY` and model name |
| WhatsApp not working | Verify `TWILIO_*` vars and phone format |
| Redis connection failed | Gracefully falls back to in-memory cache |
| OTP email not received | Check Gmail app password, not regular password |
| CORS errors on frontend | Update `ALLOWED_ORIGINS` in main.py |
| Database migrations failed | Run: `python run_migrations_direct.py` |

---

**Generated:** May 2026 | **System Status:** Production Ready ✅
