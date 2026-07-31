# SMART SHOP AI — INTERVIEW PREPARATION GUIDE
## Detailed Project Explanation for HackWithInfy Interview

---

## 📌 PROJECT OVERVIEW

**What is SmartShop AI?**

SmartShop AI is an end-to-end AI-powered price intelligence platform that helps online shoppers in India find **genuine deals** across multiple e-commerce platforms (Amazon, Flipkart, Meesho).

**The Problem It Solves:**

Every day, millions of shoppers see "SALE!" or "70% OFF!" but they don't know:
- Is this a real discount?
- Was the price higher just to show a discount?
- Should I buy now or wait?

**My Solution:**

Built an AI system that:
1. Searches products across multiple platforms
2. Tracks price history
3. Uses AI agents to analyze the data
4. Classifies deals as GENUINE_BARGAIN or FAKE_DISCOUNT
5. Sends alerts when prices drop

---

## 🏗️ ARCHITECTURE & WORKFLOW

### 5-Agent LangGraph Pipeline (The Core Innovation)

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  PRODUCT    │───▶│    PRICE        │───▶│    MARKET       │
│  FINDER     │    │    HISTORIAN    │    │    ANALYZER    │
│  (Agent 1)  │    │    (Agent 2)    │    │    (Agent 3)    │
└─────────────┘    └─────────────────┘    └─────────────────┘
        │                                        │
        ▼                                        ▼
┌─────────────┐                          ┌─────────────┐
│   AI        │◀─────────────────────────│   DEAL      │
│   PREDICTOR │                          │   SIGNAL    │
│   (Agent 4) │                          │   ENGINE    │
└─────────────┘                          └─────────────┘
        │
        ▼
┌─────────────┐
│   ALERT     │
│   MANAGER   │
│   (Agent 5) │
└─────────────┘
```

### Step-by-Step Workflow:

**Step 1: User searches for product**
- User enters: "iPhone 15 Pro"
- API receives request

**Step 2: Product Finder Agent (Agent 1)**
- Uses Tavily Search API to search Amazon, Flipkart, Croma
- Extracts: price, rating, reviews, platform, URL
- Scores products based on rating, price, platform trust
- Returns: Top 5 products with URLs

**Step 3: Price Historian Agent (Agent 2)**
- Searches for price history data
- Finds: lowest price ever, average price, current price
- Returns: Price trends and historical data

**Step 4: Market Analyzer Agent (Agent 3)**
- Searches for upcoming sales (Prime Day, Big Billion Days)
- Finds: Product-specific deals, competitor prices
- Returns: Market context and upcoming events

**Step 5: AI Predictor Agent (Agent 4)**
- Uses Cohere LLM to analyze all data
- Generates: Buy/Wait recommendation with reasoning
- Returns: Natural language prediction

**Step 6: Deal Signal Engine**
- Analyzes price patterns deterministically
- Classifies: GENUINE_BARGAIN / FAKE_DISCOUNT / NORMAL
- Returns: Signal label + confidence score

**Step 7: Alert Manager Agent (Agent 5)**
- Saves product to user's wishlist
- Schedules price monitoring
- Returns: Confirmation message

---

## 🔢 DEAL SIGNAL ENGINE (Key Feature)

### The Algorithm:

```python
# Deal Signal Rules:
if current_price < 0.9 * average_price AND current_price <= lowest_price:
    return "GENUINE_BARGAIN"  # Real deal!
elif current_price < 0.9 * previous_day_price AND previous_day_price > 1.2 * average_price:
    return "FAKE_DISCOUNT"    # Inflated price!
else:
    return "NORMAL"            # Regular price
```

### Example:
```
Product: Samsung Galaxy S24

Price History (30 days):
- Day 1: ₹85,000
- Day 15: ₹95,000 (sudden spike)
- Day 30: ₹75,000 (today)

Analysis:
- Current Price: ₹75,000
- Average (30 days): ₹82,000
- Lowest (30 days): ₹75,000
- Previous Day: ₹95,000

Result: GENUINE_BARGAIN ✓
Reason: Current price is 8.5% below average AND at 30-day low!
```

---

## ⚠️ CHALLENGES & SOLUTIONS

### Challenge 1: E-commerce websites block scraping

**Problem:**
- Amazon, Flipkart have anti-bot protection
- Simple requests get blocked
- Need real-time prices

**Solution:**
- Used `cloudscraper` library (bypasses Cloudflare)
- Added realistic headers (User-Agent, Accept-Language)
- Implemented retry logic with exponential backoff
- Fallback to Tavily search API for data
- Now tries real scraping first, falls back to mock

**Code Example:**
```python
import cloudscraper

scraper = cloudscraper.create_scraper()
response = scraper.get(url, headers=HEADERS)

# If blocked, use Tavily API instead
if response.status_code == 403:
    tavily_results = tavily.search(query=product_name)
```

---

### Challenge 2: Price extraction from HTML

**Problem:**
- Different platforms have different HTML structures
- Price can be in many formats: "₹75,000", "₹ 75000", "75,000"
- Ratings, reviews also in different formats

**Solution:**
- Created regex patterns for each platform
- Multiple patterns per field (tried sequentially)
- Filtered out EMI prices vs actual prices
- Example:
```python
# Amazon patterns
patterns = [
    r'<span class="a-price-whole">([\d,]+)',  # New format
    r'"priceAmount":([\d.]+)',                # JSON-LD
    r'<span id="priceblock_ourprice"[^>]*>₹\s*([\d,]+)',  # Old format
]
```

---

### Challenge 3: Multi-agent coordination

**Problem:**
- LangGraph agents need to share state
- Each agent produces output for next agent
- Error in one agent shouldn't crash the pipeline

**Solution:**
- Used TypedDict for shared state
- Each agent returns dict, merged into main state
- Error handling at each step
- Graceful degradation if agent fails

**State Structure:**
```python
class PriceAgentState(TypedDict):
    product_name: str
    products_found: list
    price_history: list
    ai_prediction: str
    alert_status: str
    # ... more fields
```

---

### Challenge 4: OTP authentication

**Problem:**
- Need to identify users without passwords
- OTP system needs to work reliably
- Database might not have all tables

**Solution:**
- Created in-memory OTP store (backup)
- Falls back to DB if available
- Stores in `otp_verifications` table
- If table doesn't exist, stores in users.verification_token
- If that fails too, uses memory

**Multi-layer Fallback:**
```python
def _store_otp_record(db, email, otp, expires_at):
    try:
        # Try primary table
        db.table("otp_verifications").upsert(...)
        return "otp_verifications"
    except:
        try:
            # Try users table
            db.table("users").update(...)
            return "users.verification_token"
        except:
            # Fallback to memory
            _store_otp_in_memory(email, otp, expires_at)
            return "memory"
```

---

### Challenge 5: WhatsApp notifications (Twilio)

**Problem:**
- Twilio package not installed in all environments
- WhatsApp API needs phone number format validation
- Notification should not crash main app

**Solution:**
- Graceful fallback if Twilio unavailable
- Only send if configured
- Phone number format validation
- Strips spaces, adds country code if missing

---

## 📊 TECHNICAL DECISIONS & WHY

### Why LangGraph?

**Problem:** Multi-agent systems are hard to coordinate
**Solution:** LangGraph provides:
- State management between agents
- Visual graph representation
- Error handling per node
- Easy to add/modify agents

**Why NOT just sequential functions?**
- Cleaner code organization
- Can parallelize independent tasks
- Easy to debug which agent failed
- Can reuse agents in different pipelines

---

### Why FastAPI over Flask?

- Automatic API documentation (Swagger UI)
- Type validation with Pydantic
- Async support for better performance
- Built-in CORS handling
- Modern, actively maintained

---

### Why Supabase over plain PostgreSQL?

- Real-time subscriptions (for live price updates)
- Built-in authentication
- Auto-generated APIs
- Good free tier for development
- Easy to scale

---

## 🎯 WHAT TO SAY IN INTERVIEW

### "Tell me about your project":

```
SmartShop AI is an AI-powered price intelligence platform that helps 
online shoppers find genuine deals.

The core innovation is the 5-agent LangGraph pipeline:
1. Product Finder searches across Amazon, Flipkart, Meesho
2. Price Historian fetches 30-day price history
3. Market Analyzer finds upcoming sales events
4. AI Predictor uses LLM to generate recommendations
5. Alert Manager handles notifications

The key feature is the Deal Signal Engine that classifies prices as 
GENUINE_BARGAIN or FAKE_DISCOUNT using deterministic rules based on 
price history analysis.

Tech Stack: Python, FastAPI, LangGraph, Supabase, Cohere LLM, Twilio
```

---

### "What was the biggest challenge?":

```
The biggest challenge was handling anti-bot protection from e-commerce 
sites. Amazon and Flipkart block automated requests.

I solved this by implementing a multi-layer approach:
1. Used cloudscraper library to bypass basic protection
2. Added realistic browser headers
3. Implemented exponential backoff retry logic
4. Fallback to Tavily Search API if blocked

This taught me the importance of graceful degradation and having 
backup strategies.
```

---

### "How did you design the deal-signal algorithm?":

```
The deal-signal algorithm uses simple but effective rules:

For GENUINE_BARGAIN:
- Current price must be at least 10% below 30-day average
- AND current price must be at or near the 30-day lowest

For FAKE_DISCOUNT:
- Previous day's price was inflated (20%+ above average)
- AND current price suddenly dropped (10%+ drop from previous day)

This deterministic approach is better than ML for this use case because:
1. Explainable - we can tell users exactly WHY it's a deal
2. Fast - no training required
3. Reliable - no false predictions from model errors
```

---

### "How does your system handle multiple users?":

```
The system uses Supabase for multi-user support:
1. Each user has unique ID from OTP verification
2. User's wishlists and alerts stored in database
3. API endpoints validate user session via Bearer token
4. Background scheduler processes price checks for all users

The scheduler runs every hour:
1. Fetches wishlist items for all users
2. Scrapes current prices
3. Compares with previous prices
4. Creates alert if price drop > threshold
5. Sends notification via email/WhatsApp
```

---

## 💡 LEARNINGS & TAKEAWAYS

### Technical Learnings:
1. Multi-agent system design principles
2. Web scraping anti-bot countermeasures
3. API design best practices
4. Database schema design
5. Authentication patterns

### Problem-Solving:
1. Break complex problems into smaller agents
2. Always have fallback strategies
3. Test with real-world scenarios
4. Monitor and log everything

### Product Thinking:
1. Users care about genuine deals, not just lowest price
2. Explainable AI > black-box recommendations
3. Notifications must be timely and relevant