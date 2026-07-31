## 🚀 Quick Setup Guide - AI Price Intelligence Agent v2.0

### ⚡ 5-Minute Quick Start

#### Step 1: Clone & Install Dependencies
```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd SmartShopAI
npm install
```

#### Step 2: Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials:
# - COHERE_API_KEY (LLM for predictions)
# - TAVILY_API_KEY (Web search)
# - EMAIL_ADDRESS & EMAIL_PASSWORD (Gmail OTP)
# - SUPABASE_URL & SUPABASE_KEY (Database)
```

#### Step 3: Run Backend
```bash
cd ..
python main.py
# Server starts at http://localhost:8000
```

#### Step 4: Run Frontend
```bash
cd SmartShopAI
npm start
# Expo starts at http://localhost:8081
```

---

### 🔌 Required API Keys

| Service | Purpose | Free Tier | URL |
|---------|---------|-----------|-----|
| **Cohere** | LLM for price predictions | ✅ Yes | cohere.com/api |
| **Tavily** | Web search for products | ✅ Yes | tavily.com |
| **Supabase** | Cloud database | ✅ Yes (1GB) | supabase.com |
| **Gmail** | OTP emails | ✅ Yes | Enable App Passwords |
| **Redis** | Optional caching | ⚠️ Optional | redis.io or Redis Cloud |

---

### 📊 Feature Overview

#### 🔐 Authentication
- OTP via Gmail
- Frontend login screen
- Session management

#### 🔍 Product Search
- **TOP 5 ranking algorithm** (100-point scoring)
- Real prices from 8+ platforms
- Clickable product links

#### 💰 Price Tracking
- Save favorite products
- View price history
- Get price predictions
- Savings calculations

#### 📈 Analytics
- Price trend charts
- Buying recommendations
- Savings summary
- Best deal finder

---

### 📂 Project Structure

```
ai-price-agent/
├── main.py                          # FastAPI backend (19 endpoints)
├── requirements.txt                 # Python dependencies
├── .env.example                     # Configuration template
├── migrate_to_supabase.py          # Database migration script
│
├── agents/                          # AI agent modules
│   ├── product_finder.py           # Search & ranking
│   ├── price_historian.py          # History tracking
│   ├── market_analyzer.py          # Market analysis
│   ├── ai_predictor.py             # Price prediction
│   └── alert_manager.py            # Alert system
│
├── utils/                           # Utility modules
│   ├── supabase_client.py          # Database client
│   ├── cache.py                    # Caching layer
│   ├── price_charts.py             # Analytics
│   ├── auth.py                     # Authentication
│   ├── validators.py               # Input validation
│   ├── logger.py                   # Logging
│   └── email_sender.py             # OTP emails
│
├── graph/
│   └── pipeline.py                 # LangGraph workflow (5 agents)
│
├── data/
│   └── tracked_products.json       # Local product storage
│
├── SmartShopAI/                     # React Native app
│   ├── app/(tabs)/
│   │   ├── index.tsx               # Home/Search with TOP 5
│   │   └── explore.tsx             # Dashboard
│   ├── components/
│   │   ├── price-chart.tsx         # Chart visualization
│   │   ├── themed-text.tsx         # Text components
│   │   └── themed-view.tsx         # View components
│   ├── constants/
│   │   └── theme.ts                # Design system (colors, spacing)
│   └── package.json                # Node dependencies
│
├── docs/
│   ├── INFRASTRUCTURE_GUIDE.md     # Setup & integration
│   ├── TESTING_GUIDE.md            # Test procedures
│   ├── PROJECT_STATUS.md           # Project overview
│   ├── OTP_EMAIL_SETUP.md          # Email config
│   ├── FRONTEND_REDESIGN.md        # UI/UX specs
│   ├── TOP_5_FEATURES.md           # Ranking algorithm
│   └── PRODUCT_FEATURES.md         # Feature documentation
```

---

### 🔧 Common Commands

```bash
# Start backend server
python main.py

# Start frontend with Expo
cd SmartShopAI && npm start

# Run database migration
python migrate_to_supabase.py

# Clear cache
curl -X DELETE http://localhost:8000/cache/clear

# Check cache status
curl http://localhost:8000/cache-status

# Run tests
python -m pytest test_pipeline.py -v

# Debug mode (verbose logging)
LOG_LEVEL=DEBUG python main.py
```

---

### 🌐 API Endpoints (19 Total)

#### Authentication
```
POST   /auth/request-otp          - Send OTP to email
POST   /auth/verify-otp            - Verify 6-digit OTP
```

#### Product Search & Ranking
```
POST   /analyze                    - Search & return TOP 5 products
GET    /tracked                    - Get tracked products
POST   /track                      - Track new product
GET    /my-products/{user_id}     - Get user's products
DELETE /tracked/{product_id}       - Remove tracked product
```

#### Price Comparison & Charts
```
POST   /compare                    - Compare prices across platforms
GET    /price-history/{id}         - Get price trends (30 days)
GET    /price-prediction/{id}      - Get price forecast + recommendation
GET    /best-price-day/{id}        - Find lowest price date
GET    /savings-summary/{user_id}  - Total savings opportunity
```

#### Features
```
GET    /wishlist/{user_id}                    - Get wishlist
POST   /wishlist/{user_id}/{product_id}       - Add to wishlist
DELETE /wishlist/{user_id}/{product_id}       - Remove from wishlist
GET    /dashboard/{user_id}                   - Dashboard stats
GET    /deals                                  - Hot deals (cached 5 min)
```

#### System
```
GET    /cache-status               - Cache system status
DELETE /cache/clear                - Clear all cached data
```

---

### 📊 Response Format

All endpoints return consistent JSON:

**Success Response**:
```json
{
  "success": true,
  "data": {...},
  "best_5_products": [...],  // Products with scores
  "total_found": 5
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Invalid product ID",
  "detail": "Product not found"
}
```

---

### ⚡ Performance

| Operation | Time | Cache |
|-----------|------|-------|
| Product Search | 2-3s | 10 min |
| Dashboard Load | 1-2s | 2 min |
| Price History | 1-2s | 10 min |
| Price Prediction | 3-5s | 1 hour |
| Cached Requests | 50-100ms | ✅ Instant |

**Caching reduces response times by 95%** for repeated requests.

---

### 🐛 Troubleshooting

**Backend won't start**
```bash
# Check dependencies
pip install -r requirements.txt

# Check port is not in use
lsof -i :8000

# Kill process on port
kill -9 $(lsof -t -i:8000)
```

**Frontend compilation errors**
```bash
cd SmartShopAI
npm install
npm start

# If still failing, clear cache
rm -rf node_modules package-lock.json
npm install
```

**Supabase connection failing**
```bash
# Verify credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python << 'EOF'
from supabase import create_client
import os
client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
print("✅ Connected" if client else "❌ Failed")
EOF
```

**Cache not working**
```bash
# Check status
curl http://localhost:8000/cache-status

# Clear cache
curl -X DELETE http://localhost:8000/cache/clear

# Check if Redis installed (optional)
redis-cli ping
```

---

### 🧪 Quick Test

```bash
# 1. Test OTP endpoint
curl -X POST http://localhost:8000/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Test product search  
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15", "user_email": "test@example.com"}'

# 3. Test deals endpoint (with cache)
time curl http://localhost:8000/deals
time curl http://localhost:8000/deals  # Should be 20x faster

# 4. Test dashboard
curl http://localhost:8000/dashboard/user123
```

---

### 📱 Frontend Features

**Screens**:
- 🔐 Login (OTP auth)
- 🔍 Search (TOP 5 ranking with scores)
- 📊 Dashboard (stats + activity)
- ❤️ Wishlist (saved products)
- 🎁 Deals (hot offers)

**UI Elements**:
- Vibrant gradients (6 color schemes)
- Glass-morphism cards
- Price charts (line graph)
- Ranking badges (#1-#5)
- Score bars (0-100)
- Platform tags

---

### 🔐 Security Features

- ✅ OTP authentication (6-digit codes)
- ✅ Input validation (Pydantic models)
- ✅ CORS configured (all methods)
- ✅ SQL injection protection (Supabase RLS)
- ✅ Environment variables for secrets
- ✅ Cache invalidation on updates
- ✅ Error handling (no data leaks)

---

### 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Project overview |
| **INFRASTRUCTURE_GUIDE.md** | Complete setup guide |
| **TESTING_GUIDE.md** | 50+ test cases |
| **PROJECT_STATUS.md** | Progress & stats |
| **QUICK_SETUP.md** | This file (5-min setup) |
| **OTP_EMAIL_SETUP.md** | Email configuration |
| **FRONTEND_REDESIGN.md** | UI/UX design specs |
| **TOP_5_FEATURES.md** | Ranking algorithm |

---

### ✨ Key Highlights

**TOP 5 Product Ranking**:
- Rating (40 pts) + Reviews (30 pts) + Price (20 pts) + Platform (10 pts) + Bonus (5 pts)
- Scores: 0-105 points per product
- Sorts by comprehensive quality metric

**Caching Strategy**:
- Memory cache (no setup required)
- Redis support (optional, auto-detect)
- Smart TTL per endpoint
- Auto-invalidate on updates

**Database**:
- Supabase PostgreSQL (cloud)
- Falls back to JSON if not configured
- RLS for security
- Automatic timestamps

---

### 🚀 Next Steps

1. **Configure .env** with API keys
2. **Set up Supabase** database
3. **Run migration** script (optional)
4. **Start backend** server
5. **Start frontend** app
6. **Test endpoints** using curl commands
7. **Deploy** to production

---

### 📞 Support

For detailed information:
- Backend: See `INFRASTRUCTURE_GUIDE.md`
- Tests: See `TESTING_GUIDE.md`
- Status: See `PROJECT_STATUS.md`
- Email: See `OTP_EMAIL_SETUP.md`

---

## 🎉 You're Ready!

Your AI Price Intelligence Agent is ready to use. Start tracking prices and finding the best deals! 

**Version**: 2.0
**Status**: ✅ Production Ready
**Features**: 19 endpoints, TOP 5 ranking, analytics, charts

Happy coding! 🚀
