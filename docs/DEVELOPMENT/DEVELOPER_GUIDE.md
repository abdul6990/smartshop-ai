# 📖 Quick Developer Guide

## Getting Started in 5 Minutes

### 1. Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run Backend
```bash
mkdir -p data logs
uvicorn main:app --reload
```

### 3. Test
```bash
# Visit API docs
http://localhost:8000/docs

# Test analyze endpoint
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_name":"iPhone","user_email":"test@gmail.com"}'
```

---

## Project Structure at a Glance

```
ai-price-agent/
├── main.py                 # FastAPI - Main app
├── app.py                  # Streamlit - Dashboard
├── graph/pipeline.py       # LangGraph - Orchestration
├── agents/                 # 5 AI agents
│   ├── product_finder.py   # Agent 1: Find products
│   ├── price_historian.py  # Agent 2: Price history
│   ├── market_analyzer.py  # Agent 3: Market trends  
│   ├── ai_predictor.py     # Agent 4: Buy/Wait decision
│   └── alert_manager.py    # Agent 5: Save & alert
├── utils/
│   ├── logger.py          # Logging system
│   ├── validators.py      # Input validation
│   ├── auth.py            # Auth & Supabase
│   └── email_sender.py    # Email alerts
└── SmartShopAI/           # React Native frontend
```

---

## Common Commands

```bash
# Run API
uvicorn main:app --reload

# Run dashboard
streamlit run app.py

# Run frontend
cd SmartShopAI && npm run web

# View logs
tail -f logs/smartshopai-*.log

# Test pipeline
python test_pipeline.py

# Install packages
pip install -r requirements.txt
```

---

## Key Files & Their Purpose

| File | Purpose | Key Functions |
|------|---------|---|
| `main.py` | FastAPI backend | `/analyze`, `/tracked`, `/auth/*` |
| `graph/pipeline.py` | LangGraph workflow | `run_price_pipeline()` |
| `agents/product_finder.py` | Find products | `run_product_finder()` |
| `agents/price_historian.py` | Price history | `run_price_historian()` |
| `agents/market_analyzer.py` | Market analysis | `run_market_analyzer()` |
| `agents/ai_predictor.py` | AI recommendations | `run_ai_predictor()` |
| `agents/alert_manager.py` | Save & alerts | `run_alert_manager()` |
| `utils/logger.py` | Logging | `setup_logger()`, `app_logger` |
| `utils/validators.py` | Input validation | `validate_*()` functions |
| `utils/auth.py` | Authentication | Supabase integration |

---

## Configuration (.env)

```env
# Required - Get from providers
COHERE_API_KEY=your_key
TAVILY_API_KEY=your_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

# Optional - Defaults provided
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081
LOG_LEVEL=INFO
```

---

## API Endpoints Reference

### Search
```bash
POST /analyze
{
  "product_name": "Samsung Galaxy S24",
  "user_email": "user@example.com"
}
```

### Tracking
```bash
GET /tracked                    # Get all tracked
PUT /tracked/status            # Update status
DELETE /tracked/{id}           # Delete product
```

### Authentication
```bash
POST /auth/request-otp         # Request OTP
POST /auth/verify-otp          # Verify OTP
```

### User Products
```bash
GET /my-products/{user_id}     # Get user's products
POST /track                    # Track new product
```

---

## Adding New Features

### Adding a Logger
```python
from utils.logger import app_logger

app_logger.info("Starting process")
app_logger.warning("Something unusual")
app_logger.error("Error occurred", exc_info=True)
```

### Adding Validation
```python
from utils.validators import validate_product_name

is_valid, error_msg = validate_product_name(user_input)
if not is_valid:
    raise HTTPException(status_code=422, detail=error_msg)
```

### Adding an Agent
1. Create `agents/new_agent.py`
2. Implement `run_new_agent(state: dict) -> dict`
3. Add to `graph/pipeline.py`
4. Add edge in graph

---

## Debugging

### Check Logs
```bash
tail -f logs/smartshopai-*.log
```

### API Documentation
```
http://localhost:8000/docs
```

### Test Specific Agent
```python
# In Python REPL
from agents.product_finder import run_product_finder

state = {"product_name": "iPhone", "user_email": "test@test.com"}
result = run_product_finder(state)
print(result)
```

### View Tracked Products
```bash
curl http://localhost:8000/tracked
```

---

## Error Handling Patterns

### In APIs
```python
try:
    # Validate first
    is_valid, error = validate_input(data)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)
    
    # Process
    result = process(data)
    return {"success": True, "data": result}
    
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    app_logger.error(f"Error: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal error")
```

### In Agents
```python
try:
    app_logger.info("Agent starting")
    result = agent_operation()
    app_logger.info("Agent complete")
    return result
except Exception as e:
    app_logger.error(f"Agent error: {str(e)}", exc_info=True)
    return {"error": str(e), "data": default_value}
```

---

## Performance Tips

1. **Caching**: Avoid duplicate searches
2. **Logging Level**: Set to INFO in production
3. **Batch Operations**: Group API calls when possible
4. **Error Recovery**: Fail gracefully, don't crash

---

## Git Workflow

```bash
# Create branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "feat: add new feature"

# Push
git push origin feature/new-feature

# Create PR
# Merge after review
```

---

## Testing

### Quick Test
```python
python test_pipeline.py
```

### Manual Test  
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_name":"AirPods","user_email":"test@gmail.com"}'
```

---

## Resources

- API Docs: http://localhost:8000/docs
- Logs: `./logs/`
- Config: `./.env`
- Data: `./data/`

---

## Need Help?

1. Check logs: `tail -f logs/smartshopai-*.log`
2. Check API docs: http://localhost:8000/docs
3. Check SETUP.md: Installation & configuration
4. Check IMPROVEMENTS.md: Recent changes

