# SmartShop AI - Quick Start Guide

Get the SmartShop AI price intelligence system running in minutes!

## ⚡ Prerequisites

- **Python 3.11+** (or Docker)
- **Node.js 18+** (for React Native app)
- **Git**
- **API Keys:** Cohere, Tavily, Supabase, Gmail

## 🚀 Option 1: Docker (Fastest - 5 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/smartshop-ai.git
cd smartshop-ai

# Copy environment template
cp .env.example .env

# Edit .env with your API keys and database credentials
# CRITICAL: Set POSTGRES_PASSWORD, COHERE_API_KEY, TAVILY_API_KEY, etc.

# Start all services
docker-compose up --build

# Wait 30 seconds for initialization
# Test API: curl http://localhost:8000/api/health
```

**What starts:**
- FastAPI backend on `http://localhost:8000`
- PostgreSQL database
- Redis cache
- Full LangGraph AI pipeline

---

## 🏗️ Option 2: Local Development Setup (10 minutes)

### Step 1: Clone & Navigate
```bash
git clone https://github.com/yourusername/smartshop-ai.git
cd smartshop-ai
```

### Step 2: Python Backend

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env - Add these API keys:
# - COHERE_API_KEY (from cohere.com)
# - TAVILY_API_KEY (from tavily.com)
# - SUPABASE_URL & SUPABASE_KEY (from supabase.com)
# - EMAIL_ADDRESS & EMAIL_PASSWORD (Gmail with App Passwords enabled)
```

### Step 4: Start Backend
```bash
# Run FastAPI server
python -m uvicorn main:app --reload --port 8000

# Backend ready at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Step 5: React Native Frontend (Optional)
```bash
cd SmartShopAI
npm install
npm start

# Scan QR code with Expo Go app on your phone
```

---

## 🔑 Required API Keys

| Service | Purpose | Free Tier | Setup Link |
|---------|---------|-----------|-----------|
| **Cohere** | AI price predictions | ✅ Yes (100k tokens/mo) | https://cohere.com/api |
| **Tavily** | Web search for products | ✅ Yes (1000 calls/mo) | https://tavily.com |
| **Supabase** | Cloud database | ✅ Yes (1GB storage) | https://supabase.com |
| **Gmail** | OTP authentication | ✅ Yes | Enable App Passwords |
| **Redis** | Caching (optional) | ⚠️ Optional | Self-hosted or Redis Cloud |

---

## ✅ Verify Installation

### Test Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "AI Price Intelligence API v2.0.0",
  "database": "connected"
}
```

### Test Core API
```bash
# Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Analyze product
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 15",
    "user_email": "test@example.com"
  }'
```

---

## 📁 Project Structure

```
ai-price-agent/
├── main.py                    # FastAPI backend (entry point)
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Multi-service orchestration
├── Dockerfile                 # Container configuration
├── .env.example              # Environment template
│
├── agents/                    # AI agents (5-agent pipeline)
│   ├── product_finder.py      # Search & ranking (Tavily)
│   ├── price_tracker.py       # Price history analysis
│   ├── market_analyzer.py     # Market trend detection
│   ├── ai_predictor.py        # Price prediction (Cohere)
│   └── alert_manager.py       # Alert system
│
├── graph/
│   └── pipeline.py            # LangGraph orchestration
│
├── utils/                     # Utilities
│   ├── auth.py                # OTP authentication
│   ├── supabase_client.py     # Database client
│   ├── cache.py               # Redis caching
│   ├── validators.py          # Input validation
│   ├── logger.py              # Logging system
│   └── price_charts.py        # Analytics
│
├── SmartShopAI/              # React Native frontend
│   ├── app/                  # Navigation & screens
│   ├── components/           # Reusable UI components
│   └── package.json          # Frontend dependencies
│
├── migrations/               # Database migrations
│   ├── 001_create_schema.sql
│   ├── 003_disable_rls.sql
│   └── 004_create_otp_verifications.sql
│
├── tests/                    # Test suite
│   ├── test_api.py
│   ├── test_pipeline.py
│   └── test_auth_otp_flow.py
│
└── docs/                     # Documentation
    ├── DEPLOYMENT/
    ├── SETUP/
    ├── DEVELOPMENT/
    └── ARCHIVE/
```

---

## 🔧 Common Commands

### Backend
```bash
# Run with auto-reload (development)
python -m uvicorn main:app --reload --port 8000

# Run production
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
pytest tests/ -v

# Check linting
flake8 main.py agents/ utils/
```

### Frontend
```bash
# Install dependencies
cd SmartShopAI && npm install

# Start Expo dev server
npm start

# Run on web
npm run web

# Run tests
npm test
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

### Database
```bash
# Run migrations
python run_migrations_direct.py

# Access database (if local PostgreSQL)
psql -U postgres -d smartshop_ai
```

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Supabase Connection Failed
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check internet connection
- Ensure Supabase project is active

### API Returns 401 (Unauthorized)
- OTP verification required first
- Call `/api/auth/request-otp` to get OTP
- Call `/api/auth/verify-otp` with received OTP

### Docker Build Fails
```bash
# Clean and rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

---

## 📚 Next Steps

1. **Read Full Documentation:**
   - [Deployment Guide](docs/DEPLOYMENT/DEPLOYMENT.md)
   - [Developer Guide](docs/DEVELOPMENT/DEVELOPER_GUIDE.md)
   - [Testing Guide](docs/DEVELOPMENT/TESTING_GUIDE.md)

2. **Setup API Keys:**
   - Register at Cohere.com, Tavily.com, Supabase.com
   - Add keys to `.env` file

3. **Run First Analysis:**
   - Use `/api/analyze` endpoint to search products
   - Create wishlists and price alerts
   - View recommendations dashboard

4. **Deploy to Production:**
   - See [Deployment Guide](docs/DEPLOYMENT/DEPLOYMENT.md)
   - Configure environment variables for production
   - Use Docker for reliable deployment

---

## 📞 Support & Resources

- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)
- **GitHub Issues:** Report bugs and feature requests
- **Discord Community:** Join our community chat
- **Email:** support@smartshopai.com

---

**Last Updated:** May 2026  
**Version:** 2.0.0
