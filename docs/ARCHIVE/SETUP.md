# SmartShop AI - Setup & Installation Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.12+  
- Node.js 18+ (for frontend)
- Git

### Backend Setup

1. **Clone repository**
   ```bash
   git clone <repo_url>
   cd ai-price-agent
   ```

2. **Create Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your API keys:
   - `COHERE_API_KEY` - Get from [Cohere.ai](https://cohere.ai)
   - `TAVILY_API_KEY` - Get from [Tavily](https://tavily.com)
   - `SUPABASE_URL` & `SUPABASE_KEY` - Get from [Supabase](https://supabase.io)
   - `EMAIL_ADDRESS` & `EMAIL_PASSWORD` - Gmail SMTP credentials

5. **Create data directory**
   ```bash
   mkdir -p data logs
   ```

6. **Run server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   API available at: `http://localhost:8000`  
   Docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd SmartShopAI
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run development server**
   ```bash
   npm run web
   ```
   Open: `http://localhost:19006`

### Dashboard Setup (Streamlit)

```bash
streamlit run app.py
```
Open: `http://localhost:8501`

---

## 📁 Project Structure

```
ai-price-agent/
├── main.py                 # FastAPI backend
├── app.py                  # Streamlit dashboard
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
│
├── agents/                # 5 AI agents
│   ├── product_finder.py
│   ├── price_historian.py
│   ├── market_analyzer.py
│   ├── ai_predictor.py
│   └── alert_manager.py
│
├── graph/
│   └── pipeline.py        # LangGraph orchestration
│
├── utils/
│   ├── logger.py          # Logging system
│   ├── validators.py      # Input validation
│   ├── auth.py            # Supabase auth
│   └── email_sender.py    # Gmail integration
│
├── data/
│   └── tracked_products.json
│
└── SmartShopAI/           # React Native frontend
    ├── app/
    ├── components/
    └── package.json
```

---

## 🔐 Security Configuration

### CORS Setup
Edit `.env`:
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081,https://yourdomain.com
```

### Email (Gmail SMTP)
1. Enable "Less secure apps" or
2. Generate [App Password](https://myaccount.google.com/apppasswords)
3. Use app password in `.env` as `EMAIL_PASSWORD`

---

## 🗄️ Database Setup (Supabase)

### Create Tables

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  otp TEXT,
  otp_expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tracked products table
CREATE TABLE tracked_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  product_name TEXT NOT NULL,
  last_price TEXT,
  product_url TEXT,
  platform TEXT,
  alert_sent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_user_id (user_id)
);
```

---

## 🧪 Testing

### Test the API

```bash
# Test health check
curl http://localhost:8000/

# Test product analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Samsung Galaxy S24",
    "user_email": "test@gmail.com"
  }'
```

### Run test pipeline
```bash
python test_pipeline.py
```

---

## 📊 Monitoring

### View Logs
```bash
tail -f logs/smartshopai-2026-03-30.log
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## ⚙️ Environment Variables Reference

```env
# API Keys (Required)
COHERE_API_KEY=your_key
TAVILY_API_KEY=your_key

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Supabase
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

# Server Configuration
API_PORT=8000
API_HOST=0.0.0.0
ENVIRONMENT=development

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081

# Logging
LOG_LEVEL=INFO
```

---

## 🚨 Troubleshooting

### Issue: "TAVILY_API_KEY not found"
**Solution**: Check `.env` file and ensure key is set

### Issue: "ModuleNotFoundError"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Issue: "Connection refused"
**Solution**: 
```bash
# Check if server is running
curl http://localhost:8000/

# Restart server
uvicorn main:app --reload
```

### Issue: Email not sending
**Solution**: 
1. Enable "Less secure apps" in Gmail
2. Or use Gmail App Password
3. Check `EMAIL_ADDRESS` and `EMAIL_PASSWORD`

---

## 📝 API Endpoints

### Search
- `POST /analyze` - Analyze product (returns AI prediction)

### Tracking
- `GET /tracked` - Get all tracked products
- `PUT /tracked/status` - Update product status
- `DELETE /tracked/{id}` - Delete product

### Authentication
- `POST /auth/request-otp` - Request OTP
- `POST /auth/verify-otp` - Verify OTP

### User
- `GET /my-products/{user_id}` - Get user's products
- `POST /track` - Track new product

---

## 📚 Additional Resources

- [Cohere Docs](https://docs.cohere.ai/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Expo](https://docs.expo.dev/)
- [Supabase](https://supabase.io/docs)

---

## 📞 Support

For issues, check:
1. `.env` configuration
2. API keys validity
3. Server logs: `logs/`
4. API docs: `/docs`

