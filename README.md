# SmartShop AI - AI Price Intelligence System

SmartShop AI is a 5-agent AI system that helps users find real deals on products. It tracks prices, predicts trends, and delivers personalized recommendations.

## ⚡ Quick Start (Choose One)

### Option 1: Using CLI (Simplest - 2 minutes)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env  
# Edit .env with your API keys

# 3. Try the CLI
python cli.py info              # Show system information
python cli.py health            # Check system health
python cli.py search iPhone15   # Search for a product
```

### Option 2: Docker (5 minutes)
```bash
git clone <repo>
cd smartshop-ai
cp .env.example .env
# Edit .env with API keys
docker-compose up --build

# Test: curl http://localhost:8000/api/health
```

### Option 3: Local Development with Server
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python cli.py server            # Start the backend server
# API docs: http://localhost:8000/docs
```

**Full Details:** See [QUICKSTART.md](QUICKSTART.md)

---

## 🎯 Core Features

✅ **Price Tracking** - Historical analysis and trend detection  
✅ **AI Predictions** - Cohere-powered price forecasting  
✅ **Smart Recommendations** - Personalized products with buy links  
✅ **Deal Detection** - Genuine bargain vs fake discount classification  
✅ **Alert System** - Price threshold notifications via email/WhatsApp  
✅ **OTP Authentication** - Passwordless email-based login  
✅ **Mobile App** - React Native frontend with Expo  
✅ **CLI Interface** - Command-line tools for quick access  

---

## 🖥️ CLI Commands

The `cli.py` script provides convenient access to all project features:

```bash
# System & Information
python cli.py info              # Show project info and quick links
python cli.py health            # Run system health checks

# Search & Analysis
python cli.py search iPhone15          # Search for a product
python cli.py search Samsung --email user@example.com  # Custom email

# Backend Management
python cli.py server                   # Start FastAPI backend
python cli.py server --port 9000       # Custom port
python cli.py server --reload          # Enable auto-reload

# Testing & Debugging
python cli.py test               # Run the test suite
python cli.py search iPhone15 --verbose  # Detailed output
```

---

## 🏗️ 5-Agent Architecture

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Product Finder** | Search & rank products (Tavily) | Query | Top 5 results (100-pt scoring) |
| **Price Tracker** | Historical analysis & trends | Product ID | Price history, buy/wait recommendation |
| **Market Analyzer** | Seasonal patterns & insights | Price history | Market trend classification |
| **AI Predictor** | Price forecasting (Cohere) | Historical data | 7-day price prediction |
| **Alert Manager** | Notification orchestration | Alert rules | Email/WhatsApp notifications |

**Orchestration:** LangGraph pipeline (`graph/pipeline.py`)

---

## 📡 API Endpoints (19 Total)

### Authentication
- `POST /api/auth/request-otp` - Request OTP email
- `POST /api/auth/verify-otp` - Verify OTP and get session

### Product Analysis
- `POST /api/analyze` - 5-agent analysis (TOP 5 products)
- `GET /api/health` - Health check

### Price Tracking
- `GET /api/price-tracker/history` - Historical prices
- `GET /api/price-tracker/recommendation` - Buy/wait recommendation
- `POST /api/price-tracker/track` - Record new price

### Wishlist Management
- `GET /api/wishlists` - User's wishlists
- `POST /api/wishlists` - Create wishlist
- `POST /api/wishlists/{id}/items` - Add to wishlist
- `DELETE /api/wishlists/{id}/items/{item_id}` - Remove from wishlist

### Price Alerts
- `GET /api/price-alerts` - User's price alerts
- `POST /api/price-alerts` - Create price alert
- `DELETE /api/price-alerts/{id}` - Delete alert

### Recommendations
- `GET /api/recommendations/personalized` - AI recommendations for user
- `GET /api/recommendations/category` - Category trends

### Analytics & Dashboard
- `GET /api/dashboard/{user_id}` - Full dashboard
- `GET /api/charts/price` - Price charts

**API Docs:** Visit `http://localhost:8000/docs` (Swagger UI)

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI (Python 3.11) | REST API & orchestration |
| **Database** | Supabase PostgreSQL | Persistent storage |
| **Cache** | Redis 7 | Session & price cache |
| **LLM** | Cohere | Price predictions |
| **Search** | Tavily API | Product discovery |
| **Frontend** | React Native + Expo | Mobile app |
| **Orchestration** | LangGraph | 5-agent pipeline |
| **Notifications** | Gmail, Twilio | Email/WhatsApp alerts |
| **Infrastructure** | Docker Compose | Local & cloud deployment |
| **CLI** | Click | Command-line interface |

---

## 📁 Project Structure

```
ai-price-agent/
├── cli.py                     # Command-line interface
├── main.py                    # FastAPI entry point (850 lines)
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # PostgreSQL, Redis, API
├── Dockerfile                 # Container config
│
├── agents/                    # 5-agent pipeline
│   ├── product_finder.py      # Tavily search & ranking
│   ├── price_tracker.py       # History & analysis
│   ├── market_analyzer.py     # Trends & patterns
│   ├── ai_predictor.py        # Cohere predictions
│   └── alert_manager.py       # Notifications
│
├── graph/pipeline.py          # LangGraph orchestration
├── utils/                     # Shared utilities
├── migrations/                # Database schema
├── tests/                     # Test suite
├── SmartShopAI/              # React Native app
└── docs/                      # Full documentation
```

---

## ✅ Verification & Tests

Run the verification suite to ensure everything is working:

```bash
# Full system check
python cli.py health

# Run test suite
python cli.py test

# Or manually run pytest
python -m pytest tests/ -v
```

**Test Status:**
- ✅ 7/7 unit tests passing (auth, deal signals)
- ✅ Pipeline execution verified end-to-end
- ✅ Supabase connection active
- ✅ All agents functional

---

## 📚 Documentation

| Guide | Purpose |
|-------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup & local dev |
| [docs/DEPLOYMENT/DEPLOYMENT.md](docs/DEPLOYMENT/DEPLOYMENT.md) | Production deployment |
| [docs/DEVELOPMENT/DEVELOPER_GUIDE.md](docs/DEVELOPMENT/DEVELOPER_GUIDE.md) | Code architecture |
| [docs/DEVELOPMENT/TESTING_GUIDE.md](docs/DEVELOPMENT/TESTING_GUIDE.md) | Running tests |
| [docs/DEVELOPMENT/API_DOCUMENTATION.md](docs/DEVELOPMENT/API_DOCUMENTATION.md) | API reference |
| [docs/SETUP/OTP_SETUP.md](docs/SETUP/OTP_SETUP.md) | Email OTP configuration |

1. **Cohere** (https://cohere.com/api) - LLM for price predictions
2. **Tavily** (https://tavily.com) - Product search  
3. **Supabase** (https://supabase.com) - Cloud database
4. **Gmail** - OTP emails (enable App Passwords)
5. **Redis** - Optional caching

---

## ✅ Verification

```bash
# Test backend
curl http://localhost:8000/api/health

# View API docs
# Open http://localhost:8000/docs in browser

# Run tests
pytest tests/ -v

# Docker health
docker-compose ps
docker-compose logs api
```

---

## 🔐 Authentication

**OTP-only** passwordless system:
1. User requests OTP → email sent via Gmail SMTP
2. User verifies OTP → session created
3. Bearer token included in Authorization header for protected routes

```bash
# Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Verify OTP (check email for code)
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "otp": "123456"}'
```

---

## 📊 Deal Classification Logic

Products automatically classified as:

- **GENUINE_BARGAIN** - Current price < 90% of 30-day average AND lowest in period
- **FAKE_DISCOUNT** - Inflated baseline then discounted (detected via logic)
- **NORMAL** - Regular market price

---

## 🚀 Deployment

### Docker (Recommended)
```bash
docker-compose up -d
```
Starts: API (8000), PostgreSQL (5432), Redis (6379)

### Cloud Deployment
See [docs/DEPLOYMENT/DEPLOYMENT.md](docs/DEPLOYMENT/DEPLOYMENT.md) for:
- Railway
- Render
- AWS EC2
- DigitalOcean

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_pipeline.py -v

# With coverage
pytest --cov=agents --cov=utils tests/
```

---

## 📞 Support

- **Issues:** GitHub Issues
- **Docs:** Full docs in `docs/` directory
- **API Docs:** `http://localhost:8000/docs`

---

## 📝 Environment Variables

See `.env.example` for template. Critical variables:

```bash
# Database (Docker)
POSTGRES_PASSWORD=<secure_password>
POSTGRES_USER=smartshop_user
POSTGRES_DB=smartshop_ai

# APIs
COHERE_API_KEY=<key>
TAVILY_API_KEY=<key>
SUPABASE_URL=<url>
SUPABASE_KEY=<key>

# Email OTP
EMAIL_ADDRESS=<gmail@gmail.com>
EMAIL_PASSWORD=<app_password>

# Frontend
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081

# Environment
ENVIRONMENT=development  # or production
```

---

**Version:** 2.0.0  
**Last Updated:** May 2026  
**License:** MIT  
**Status:** Production-Ready ✅
