# SmartShop AI - AI-Powered Price Tracking & Recommendations

An intelligent e-commerce price tracking and personal shopping assistant system that helps users find the best deals, track price trends, and get personalized product recommendations.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![React Native](https://img.shields.io/badge/React%20Native-Expo-blue?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)

## 🎯 Features

### 💰 Smart Price Tracking
- **Real-time Monitoring**: Track prices across Amazon, Flipkart, eBay, and more
- **Price History**: 30-day rolling price history with trend analysis
- **Savings Detection**: Automatically identify when products drop in price
- **Trend Forecasting**: Predict future price movements

### 🤖 AI Recommendations
- **Personalized Suggestions**: ML-powered recommendations based on browsing history
- **Wishlist Alerts**: Notify when wishlist items go on sale
- **Bundle Suggestions**: Smart product bundles with savings
- **Category Trends**: Discover trending products in categories you like

### 🔔 Intelligent Alerts
- **Price Drop Alerts**: Get notified when prices drop 10%+
- **Price Milestone Alerts**: Alert when reaching your target price
- **Back in Stock**: Know immediately when out-of-stock items return
- **Deal Expiring**: Don't miss limited-time offers

### 📊 Analytics Dashboard
- Price trend visualization with interactive charts
- Spending patterns and savings analysis
- Recommendation precision metrics
- User engagement analytics

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone and setup
git clone https://github.com/yourusername/smartshop-ai.git
cd smartshop-ai
cp .env.example .env

# Start all services
docker-compose up -d

# API available at http://localhost:8000
curl http://localhost:8000/health
```

### Local Setup
```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn api:app --reload

# Mobile App
cd SmartShopAI
npm install
npm start
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Comprehensive setup & architecture
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[FEATURES.md](FEATURES.md)** - Feature deep-dive with examples
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

## 🏗️ Architecture

```
┌────────────────────────────────────────────────┐
│         SmartShop AI System Architecture       │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Mobile   │  │   Web    │  │ Admin    │    │
│  │   App    │  │Dashboard │  │ Panel    │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │             │           │
│       └─────────────┼─────────────┘           │
│                     │                         │
│         ┌───────────▼───────────┐             │
│         │    FastAPI Backend    │             │
│         │  • Price Tracker      │             │
│         │  • Recommendations    │             │
│         │  • Alert Manager      │             │
│         └───────────┬───────────┘             │
│                     │                         │
│     ┌───────────────┼───────────────┐         │
│     │               │               │         │
│  ┌──▼──┐      ┌─────▼────┐    ┌────▼────┐   │
│  │Redis│      │Supabase  │    │Background│  │
│  │Cache│      │Database  │    │Jobs     │   │
│  └─────┘      └──────────┘    └─────────┘   │
│                                               │
└────────────────────────────────────────────────┘
```

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/price-tracker/history` | GET | Get price history |
| `/price-tracker/recommendation` | GET | Buy recommendation |
| `/price-tracker/track` | POST | Track price change |
| `/recommendations/personalized` | GET | Get recommendations |
| `/recommendations/category-trends` | GET | Category trends |
| `/alerts/user` | GET | Get user alerts |
| `/alerts/{id}/read` | POST | Mark alert read |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for full reference.

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + Supabase
- **Cache**: Redis
- **Job Scheduler**: APScheduler
- **Web Scraping**: BeautifulSoup + Selenium
- **Testing**: Pytest

### Frontend (Mobile)
- **Framework**: React Native + Expo
- **Language**: TypeScript
- **State Management**: React Hooks
- **HTTP**: Fetch API
- **UI Components**: React Native built-ins

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Deployment**: AWS ECS, Google Cloud Run, or Heroku
- **Monitoring**: CloudWatch, Datadog, or Sentry
- **Logging**: Cloud Logging or ELK Stack

## 📦 Project Structure

```
smartshop-ai/
├── agents/                      # AI/ML agents
│   ├── price_tracker.py        # Price monitoring
│   ├── recommendation_engine.py # Recommendations
│   ├── alert_manager.py        # Alerts
│   └── market_analyzer.py      # Market analysis
├── SmartShopAI/                # React Native app
│   ├── components/             # UI components
│   ├── hooks/                  # React hooks
│   └── app/                    # App screens
├── utils/                       # Shared utilities
│   ├── logger.py
│   ├── supabase_client.py
│   ├── email_sender.py
│   └── auth.py
├── graph/                       # Data pipeline
│   └── pipeline.py
├── tests/                       # Test suites
│   ├── test_price_tracker.py
│   ├── test_recommendation_engine.py
│   └── test_api.py
├── api.py                       # FastAPI server
├── Dockerfile                   # Container config
├── docker-compose.yml           # Multi-container setup
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test coverage
pytest --cov=agents --cov=utils

# Specific test file
pytest tests/test_price_tracker.py -v

# Test with markers
pytest -m integration
```

## 🔐 Security

- ✅ Environment variables for secrets
- ✅ JWT authentication
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ SQL injection prevention (via ORM)
- ✅ HTTPS/TLS support
- ✅ Data encryption at rest

## 📈 Performance

| Metric | Target | Status |
|--------|--------|--------|
| Price Tracking API Response | < 200ms | ✅ |
| Recommendation Generation | 2-5s | ✅ |
| Alert Delivery | < 5 minutes | ✅ |
| Database Queries | < 100ms | ✅ |
| Cache Hit Rate | > 80% | ✅ |

## 📊 Monitoring

- **Application Errors**: Sentry
- **System Metrics**: CloudWatch/Datadog
- **Logs**: Cloud Logging/ELK
- **APM**: New Relic/Datadog
- **Uptime**: StatusPage

## 🚢 Deployment

Deployment guides available for:
- **AWS ECS** - Recommended for production
- **Google Cloud Run** - Serverless option
- **Heroku** - Quick deployment
- **Docker** - Any container orchestration platform

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 💰 Pricing Estimates

| Platform | Monthly Cost | Notes |
|----------|-------------|-------|
| AWS | ~$95 | EC2 + RDS + ElastiCache |
| GCP | ~$110 | Cloud Run + Cloud SQL + Memorystore |
| Heroku | ~$130 | Dynos + PostgreSQL + Redis |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/description`
3. Make changes and test
4. Submit pull request

## 📋 Roadmap

- [ ] Machine learning price predictions
- [ ] Voice-based alerts
- [ ] Real-time price comparison widget
- [ ] Cryptocurrency price tracking
- [ ] Social features (price sharing)
- [ ] Advanced analytics dashboard
- [ ] Mobile app native modules
- [ ] Integration with more e-commerce platforms

## 🐛 Known Issues

None currently! Please report issues on [GitHub Issues](https://github.com/yourusername/smartshop-ai/issues).

## 📞 Support

- 📧 **Email**: support@smartshop.ai
- 💬 **Discord**: [Join Community](https://discord.gg/smartshop)
- 📖 **Docs**: [https://docs.smartshop.ai](https://docs.smartshop.ai)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/smartshop-ai/issues)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ✨ Highlights

- ⚡ Fast API responses with Redis caching
- 🤖 AI-powered intelligent recommendations
- 📱 Cross-platform mobile app
- 🔄 Real-time price tracking
- 🎯 Personalized user experience
- 🐳 Docker containerization
- 📊 Comprehensive documentation
- 🧪 Full test coverage

---

**Ready to save money while shopping smarter?** 🛍️

Get started with [QUICKSTART.md](QUICKSTART.md) or explore the full [documentation](/).

Made with ❤️ by the SmartShop AI team.
