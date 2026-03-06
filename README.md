#  SmartShop AI — AI Price Intelligence Agent

> AI-powered price tracking system that analyzes Amazon prices, predicts the best time to buy, and sends real-time email alerts.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)
![React Native](https://img.shields.io/badge/React%20Native-Expo-purple)

## 🎯 What It Does

1. User searches any product by name
2. **5 AI agents** work together to analyze it
3. Returns current price, historical low, and AI prediction
4. Sends personalized email alert
5. Tracks all products in a dashboard

## 🤖 The 5 AI Agents

| Agent | Job |
|-------|-----|
| 🔍 Product Finder | Searches Amazon India for the product |
| 📊 Price Historian | Finds historical prices and lowest ever |
| 📰 Market Analyzer | Detects upcoming sales (Prime Day, Big Billion Days) |
| 🤖 AI Predictor | Gives buy/wait recommendation with reasoning |
| 🔔 Alert Manager | Saves to tracker and sends email alert |

## 🏗️ Architecture
```
React Native Frontend (Expo)
         ↓
FastAPI Backend (Python)
         ↓
LangGraph Pipeline
         ↓
Agent 1 → Agent 2 → Agent 3 → Agent 4 → Agent 5
         ↓
Cohere LLM + Tavily Search
```

## 🛠️ Tech Stack

- **Agent Framework:** LangGraph
- **LLM:** Cohere command-r-plus
- **Search:** Tavily API
- **Backend:** FastAPI + Uvicorn
- **Frontend:** React Native (Expo Web)
- **Email:** Gmail SMTP
- **Storage:** JSON

## 🚀 How To Run

### Backend
```bash
# Clone the repo
git clone https://github.com/abdul6990/smartshop-ai.git
cd smartshop-ai

# Install dependencies
pip install -r requirements.txt

# Add your API keys to .env
COHERE_API_KEY=your-key
TAVILY_API_KEY=your-key
EMAIL_ADDRESS=your-gmail
EMAIL_PASSWORD=your-app-password

# Run the API
uvicorn main:app --reload
```

### Frontend
```bash
cd SmartShopAI
npm install
npm run web
```

## 📸 Demo

### Search Screen
- Enter product name
- AI agents analyze in real-time
- Get buy/wait recommendation

### Tracker Screen  
- View all tracked products
- Update status (Tracking/Purchased/Cancelled)
- See AI predictions history

## 🎯 Sample Output
```
Product: Samsung Galaxy S24
Current Price: ₹43,499
Historical Low: ₹39,999
Recommendation: WAIT - Amazon Great Indian 
Festival Sale starts in 3 weeks, expected 
15-20% discount based on historical patterns
```

## 👨‍💻 Author

**Syed Abdul Rehaman**  
AI Automation Engineer  
github.com/abdul6990