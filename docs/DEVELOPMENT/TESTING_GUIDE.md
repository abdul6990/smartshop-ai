## Testing Guide: Caching, Supabase & Price Charts

### 📋 Test Checklist

#### 1. Cache System Tests

**Test 1.1: Memory Cache Basic Operations**
```bash
# Start backend
python main.py

# In terminal, test cache endpoints
curl http://localhost:8000/cache-status
# Expected: {"success": true, "cache_type": "Memory", ...}

# Clear cache
curl -X DELETE http://localhost:8000/cache/clear
# Expected: {"success": true, "message": "Cache cleared successfully"}
```

**Test 1.2: Cache Hit Performance**
```bash
# First call (cache miss) - should be slower
time curl http://localhost:8000/deals
# Expected: ~1000ms, returns deals list

# Second call (cache hit) - should be much faster
time curl http://localhost:8000/deals
# Expected: ~50ms, same data

# Verify cache is working by checking backend logs
# Should see: "🔄 Cache HIT: deals:get_trending_deals"
```

**Test 1.3: Cache Expiration**
```bash
# Get deals (cached for 5 min)
curl http://localhost:8000/deals

# Wait 5 minutes, then request again
sleep 300
curl http://localhost:8000/deals
# Expected: Cache miss, fresh data fetched
```

---

#### 2. Supabase Integration Tests

**Prerequisites**: 
- Set `SUPABASE_URL` and `SUPABASE_KEY` in .env
- Create tables in Supabase (see INFRASTRUCTURE_GUIDE.md)

**Test 2.1: Add Tracked Product**
```bash
curl -X POST http://localhost:8000/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "product_name": "iPhone 15 Pro",
    "price": "₹99,999",
    "url": "https://amazon.in/iphone15",
    "platform": "Amazon"
  }'
# Expected: {"success": true, "message": "Product tracked!"}

# Verify in Supabase dashboard:
# - tracked_products table should have the new entry
# - user_id, title, price, platform fields populated
# - created_at timestamp auto-filled
```

**Test 2.2: Get User Products**
```bash
curl http://localhost:8000/my-products/test_user_123
# Expected: {"success": true, "products": [...]}
# Should return the product added in Test 2.1
```

**Test 2.3: Migration Script**
```bash
# Create test JSON if needed
cd data
cat > tracked_products.json << EOF
[
  {
    "user_id": "migration_test",
    "title": "Test Product",
    "price": "₹5,000",
    "platform": "Amazon",
    "url": "https://example.com"
  }
]
EOF

# Run migration
cd ..
python migrate_to_supabase.py
# Expected:
# ✅ Migrating tracked products...
# ✅ Migrated: Test Product
# ✅ Backup saved to: data/tracked_products.backup.*.json
```

---

#### 3. Price Charts & Analytics Tests

**Test 3.1: Get Price History (No Data)**
```bash
curl http://localhost:8000/price-history/999
# Expected: {"success": true, "status": "no_data", "message": "No price history available"}
```

**Test 3.2: Log Prices and Get History**
```bash
# Using Python script to log sample prices
python << 'EOF'
from utils.supabase_client import db

# Log some sample prices
for i in range(5):
    db.log_price(product_id=1, price=f"₹{50000 - i*1000}", platform="Amazon")

print("✅ Logged 5 price points")
EOF

# Now fetch history
curl http://localhost:8000/price-history/1?days=30
# Expected: {"success": true, "min_price": 46000, "max_price": 50000, ...}
```

**Test 3.3: Price Prediction**
```bash
curl http://localhost:8000/price-prediction/1
# Expected: {"success": true, "predicted_price": ..., "trend": "down", "confidence": "low"}
```

**Test 3.4: Best Price Day**
```bash
curl http://localhost:8000/best-price-day/1?days=30
# Expected: {"success": true, "best_price_day": {"date": "2024-01-15", "price": 46000, "savings": 4000}}
```

**Test 3.5: Savings Summary**
```bash
curl "http://localhost:8000/savings-summary/test_user_123"
# Expected: 
# {
#   "success": true,
#   "total_potential_savings": 15000,
#   "products_tracked": 3,
#   "products_with_history": 2
# }
```

---

#### 4. Integration Tests (Full Flow)

**Test 4.1: Search → Track → View Charts**
```bash
# 1. Search for product
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15", "user_email": "test@example.com"}'

# 2. Track the best product
curl -X POST http://localhost:8000/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "integration_test",
    "product_name": "iPhone 15 Pro",
    "price": "₹99,999",
    "url": "https://amazon.in/iphone15pro",
    "platform": "Amazon"
  }'

# 3. View dashboard (cached)
curl http://localhost:8000/dashboard/integration_test

# 4. View price history
curl http://localhost:8000/price-history/1

# Expected: All endpoints return success, data flows through system
```

**Test 4.2: Cache Invalidation**
```bash
# 1. Get deals (cached)
curl http://localhost:8000/deals > response1.json

# 2. Update deals (this should invalidate cache)
curl -X POST http://localhost:8000/deals-update \
  -H "Content-Type: application/json" \
  -d '{"deals": []}'

# 3. Get deals again (should be fresh, not cached)
curl http://localhost:8000/deals > response2.json

# Compare timestamps - should be different
echo "Response 1 timestamp:"; cat response1.json | jq '.timestamp'
echo "Response 2 timestamp:"; cat response2.json | jq '.timestamp'
```

---

#### 5. Frontend Component Tests

**Test 5.1: Install Dependencies**
```bash
cd SmartShopAI
npm install react-native-chart-kit
# Expected: Package installed successfully
```

**Test 5.2: Import Price Chart Component**
```bash
# Edit explore.tsx or dashboard and add:
import PriceChart from '@/components/price-chart';

# Then use in component:
<PriceChart 
  productId={1}
  productName="iPhone 15"
  days={30}
/>
```

**Test 5.3: Build & Run**
```bash
# From SmartShopAI directory
npm start
# Expected: Expo running successfully with price chart displayed
```

---

#### 6. Performance Tests

**Test 6.1: Response Time Comparison**
```bash
# Clear cache first
curl -X DELETE http://localhost:8000/cache/clear

# Measure uncached request
time curl http://localhost:8000/deals
# Note the time (should be ~1-2 seconds)

# Immediate second request (should be cached)
time curl http://localhost:8000/deals
# Note the time (should be <100ms)

# Expected: 20x faster with caching
```

**Test 6.2: Concurrent Requests**
```bash
# Test cache under load
for i in {1..10}; do
  curl http://localhost:8000/deals &
done
wait

# Expected: All requests complete quickly (~50ms each)
# Shows cache working properly under concurrency
```

---

#### 7. Error Handling Tests

**Test 7.1: Invalid Product ID**
```bash
curl http://localhost:8000/price-history/-1
# Expected: {"error": "Invalid product ID"}
```

**Test 7.2: Missing Supabase Credentials**
```bash
# Unset Supabase env vars
unset SUPABASE_URL SUPABASE_KEY

# Restart server and try
curl -X POST http://localhost:8000/track \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "product_name": "Test", "price": "₹1000", "url": "http://test.com"}'

# Expected: Falls back to JSON or returns warning
```

**Test 7.3: Redis Connection Failure**
```bash
# If Redis configured, stop Redis service
# Make request
curl http://localhost:8000/deals

# Expected: Falls back to memory cache, still works
```

---

#### 8. Data Consistency Tests

**Test 8.1: Verify Price History Data**
```bash
# Log prices with specific values
python << 'EOF'
from utils.supabase_client import db
import time

for price in [50000, 49000, 48000, 48500, 47000]:
    db.log_price(1, f"₹{price}", "Amazon")
    time.sleep(1)

# Fetch and verify
history = db.get_price_history(1)
print(f"Logged: {len(history)} prices")
for h in history:
    print(f"  {h['price']} - {h['platform']}")
EOF
```

**Test 8.2: Verify Cache Consistency**
```bash
# Make request A
result_a = curl http://localhost:8000/dashboard/test_user | jq '.stats.total_saved'

# Verify same result on second request (cached)
result_b = curl http://localhost:8000/dashboard/test_user | jq '.stats.total_saved'

# Expected: result_a == result_b (within 2 min cache window)
```

---

#### 9. Monitoring & Debugging

**Test 9.1: Cache Status**
```bash
curl http://localhost:8000/cache-status
# Expected:
# {
#   "success": true,
#   "cache_type": "Memory",
#   "cache_size": 12,
#   "status": "healthy"
# }
```

**Test 9.2: Enable Debug Logging**
```bash
# Edit .env
export LOG_LEVEL=DEBUG

# Restart server and make requests
python main.py

# Expected: See cache hit/miss messages in console
# 🔄 Cache HIT: deals:get_trending_deals
# 🔄 Cache MISS (computed): deals:get_trending_deals
```

---

### ✅ Test Report Template

```
| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| 1.1 | Cache Status | ✅ PASS | Memory cache detected |
| 1.2 | Cache Hit | ✅ PASS | 20x speed improvement |
| 1.3 | Cache Expiration | ✅ PASS | TTL working |
| 2.1 | Add Product | ✅ PASS | Supabase insert works |
| 2.2 | Get Products | ✅ PASS | Query returns correct data |
| 3.1 | Price History | ✅ PASS | Analytics working |
| 3.2 | Price Prediction | ✅ PASS | ML model running |
| 4.1 | Full Integration | ✅ PASS | End-to-end flow working |
| 5.1 | Frontend Chart | ✅ PASS | Component renders |
| 6.1 | Performance | ✅ PASS | 50ms response times |
```

---

### 🔍 Debugging Tips

**If cache not working**:
```bash
# Check if Redis running
redis-cli ping
# If missing: redis-cli not found means Redis not installed

# Check memory cache size growing
curl http://localhost:8000/cache-status
# cache_size should increase then stabilize
```

**If Supabase not connecting**:
```bash
# Verify credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test Supabase connection
python << 'EOF'
from supabase import create_client
client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
print("✅ Connected" if client else "❌ Failed")
EOF
```

**If price charts not displaying**:
```bash
# Check component import
grep "react-native-chart-kit" SmartShopAI/components/price-chart.tsx

# Verify package installed
npm list react-native-chart-kit
```

---

### 📊 Expected Output Examples

**Cache Status**:
```json
{
  "success": true,
  "cache_type": "Memory",
  "cache_size": 5,
  "status": "healthy"
}
```

**Price History**:
```json
{
  "success": true,
  "product_id": 1,
  "days": 30,
  "min_price": 46000,
  "max_price": 50000,
  "avg_price": 48000,
  "trend": "down",
  "change_percent": -8.0,
  "data_points": [
    {"date": "2024-01-15", "price": 50000, "platform": "Amazon"},
    {"date": "2024-01-16", "price": 49000, "platform": "Amazon"}
  ]
}
```

**Price Prediction**:
```json
{
  "success": true,
  "current_avg": 48000,
  "predicted_price": 47000,
  "trend": "down",
  "confidence": "high",
  "recommendation": "🔥 Great time to buy - Price dropping!"
}
```

---

### 🚀 Running All Tests

```bash
#!/bin/bash

echo "🧪 Running All Tests..."
echo "===================="

# 1. Start server
python main.py &
SERVER_PID=$!
sleep 2

# 2. Run tests
python -m pytest test_pipeline.py -v

# 3. Test caching
curl http://localhost:8000/deals
curl http://localhost:8000/cache-status

# 4. Test Supabase
curl -X POST http://localhost:8000/track \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "product_name": "Test", "price": "₹1000", "url": "http://test.com"}'

# 5. Test charts
curl http://localhost:8000/price-history/1

# 6. Cleanup
kill $SERVER_PID

echo "✅ All tests completed!"
```

---

**Status**: All tests should PASS before production deployment ✅
