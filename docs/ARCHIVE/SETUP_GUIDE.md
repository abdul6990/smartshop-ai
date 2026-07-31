# SmartShop AI - Complete Setup Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SmartShop AI System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐         ┌──────────────────────┐       │
│  │   Mobile App (RN)    │         │   Web Dashboard      │       │
│  │  • Recommendations   │         │   • Admin Panel      │       │
│  │  • Price Tracking    │         │   • Analytics        │       │
│  │  • Alerts            │         │   • Settings         │       │
│  └──────────┬───────────┘         └──────────┬───────────┘       │
│             │                                 │                    │
│             └─────────────┬───────────────────┘                    │
│                           │                                        │
│              ┌────────────▼────────────┐                          │
│              │   FastAPI Backend       │                          │
│              │   • Price Tracker       │                          │
│              │   • Recommendations     │                          │
│              │   • Alert Manager       │                          │
│              └────────────┬────────────┘                          │
│                           │                                        │
│       ┌───────────────────┼───────────────────┐                  │
│       │                   │                   │                   │
│   ┌───▼──┐          ┌─────▼────┐        ┌────▼────┐              │
│   │Redis │          │Supabase  │        │Background │            │
│   │Cache │          │Database  │        │Jobs      │            │
│   └──────┘          └──────────┘        └──────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (for mobile app)
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional)

## Backend Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/smartshop-ai.git
cd smartshop-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your Supabase credentials and API keys
```

### 5. Database Setup
Option A: Using Supabase (Recommended)
```bash
# Create Supabase project at https://supabase.com
# Copy URL and Key to .env
```

Option B: Using PostgreSQL Locally
```bash
postgres=# CREATE DATABASE smartshop_ai;
```

### 6. Run Database Migrations
```bash
python -c "from utils.db import init_db; init_db()"
```

### 7. Start Backend Server
```bash
uvicorn api:app --reload --port 8000
```

Server will be available at `http://localhost:8000`

## Frontend Setup

### Mobile App (React Native / Expo)

#### 1. Install Dependencies
```bash
cd SmartShopAI
npm install
# or yarn install
```

#### 2. Configure API URL
Create `SmartShopAI/.env.local`:
```
EXPO_PUBLIC_API_URL=http://your-api-url:8000/api
```

#### 3. Start Development Server
```bash
npm start
```

Follow Expo CLI instructions to run on iOS/Android emulator or physical device.

### Web Dashboard (React)

#### 1. Setup React App
```bash
npx create-react-app smartshop-dashboard
cd smartshop-dashboard
npm install axios chart.js react-chartjs-2
```

#### 2. Configure API Endpoint
```javascript
// config.js
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

#### 3. Start Development Server
```bash
npm start
```

## Docker Setup (All-in-One)

### Build and Run with Docker Compose

```bash
# Copy environment template
cp .env.example .env

# Build and run services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

Services running:
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Useful Docker Commands

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (data)
docker-compose down -v

# Rebuild services
docker-compose build --no-cache

# Run migrations
docker-compose exec api python -c "from utils.db import init_db; init_db()"

# Access database
docker-compose exec postgres psql -U smartshop_user -d smartshop_ai
```

## Project Structure

```
smartshop-ai/
├── agents/                 # AI/ML agents
│   ├── price_tracker.py    # Price tracking logic
│   ├── recommendation_engine.py
│   ├── alert_manager.py
│   └── market_analyzer.py
├── graph/                  # Data pipeline
│   └── pipeline.py         # ETL workflows
├── utils/                  # Utilities
│   ├── logger.py
│   ├── supabase_client.py
│   ├── email_sender.py
│   └── auth.py
├── SmartShopAI/            # React Native mobile app
│   ├── components/         # React components
│   ├── hooks/              # Custom React hooks
│   ├── app/                # App screens
│   └── package.json
├── api.py                  # FastAPI server
├── main.py                 # CLI entry point
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-container setup
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# API
PORT=8000
DEBUG=True
JWT_SECRET=your-secret-key

# Email Alerts
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=app-password

# Feature Flags
ENABLE_PRICE_PREDICTIONS=True
ENABLE_BUNDLE_RECOMMENDATIONS=True
```

### Database Schema

Core tables:
- `users`: User accounts
- `products`: Product catalog
- `product_prices`: Price history
- `product_platforms`: E-commerce platforms
- `recommendations`: Generated recommendations cache
- `user_alerts`: Alert configurations
- `browsing_history`: User activity tracking

## Running Tests

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Coverage Report
```bash
pytest --cov=agents --cov=utils
```

## Price Tracking Pipeline

The background pipeline runs price tracking jobs:

```python
# Schedule automatic price updates
from graph.pipeline import schedule_price_tracking

# Run every 6 hours
schedule_price_tracking(interval_hours=6)
```

### Supported E-commerce Platforms
- Amazon
- Flipkart
- eBay
- Myntra
- Custom integrations

## Performance Optimization

### Redis Caching
```python
from utils.cache import get_cached, set_cached

# Cache recommendations for 1 hour
set_cached(f"recs:{user_id}", recommendations, ttl=3600)
```

### Database Indexing
Key indexes for performance:
- `product_id` on price tables
- `user_id` on alerts/recommendations
- `created_at` for time-based queries

## Monitoring & Logging

### View Logs
```bash
# Backend logs
docker-compose logs -f api

# Application logs (file)
tail -f logs/app.log

# Real-time log search
grep "price_drop" logs/app.log
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in .env
- [ ] Configure `JWT_SECRET` with strong value
- [ ] Setup SSL/HTTPS certificates
- [ ] Configure environment for production Supabase
- [ ] Setup email service for alerts
- [ ] Configure CDN for static assets
- [ ] Setup monitoring/alerting

### Deploy to AWS
```bash
# Using AWS ECS
aws ecs create-service --cluster smartshop --service-name api --task-definition smartshop-api

# Using AWS Lambda
serverless deploy
```

### Deploy to Google Cloud
```bash
# Deploy to Cloud Run
gcloud run deploy smartshop-api --source .
```

### Deploy to Heroku
```bash
heroku create smartshop-api
git push heroku main
```

## Troubleshooting

### Issue: API not connecting to database
```bash
# Check Supabase credentials
export SUPABASE_URL=your-url
export SUPABASE_KEY=your-key

# Test connection
python -c "from utils.supabase_client import db; print(db.table('users').select('count').execute())"
```

### Issue: Slow recommendations
```bash
# Clear Redis cache
redis-cli FLUSHDB

# Rebuild recommendation cache
python -m agents.recommendation_engine --rebuild
```

### Issue: Email alerts not sending
```bash
# Check SMTP configuration
python -c "from utils.email_sender import send_test_email; send_test_email()"
```

## Contributing

1. Create feature branch: `git checkout -b feature/description`
2. Make changes and test
3. Submit pull request
4. Code will be reviewed and merged

## Support & Community

- **Discord**: discord.gg/smartshop
- **GitHub Issues**: For bug reports
- **Email**: support@smartshop.ai
- **Documentation**: https://docs.smartshop.ai

## License

MIT License - see LICENSE file for details
