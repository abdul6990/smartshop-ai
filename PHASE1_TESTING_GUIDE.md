# Phase 1 - Testing Guide

## Quick Start Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Backend
```bash
python main.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ APScheduler started successfully
```

### 3. Start Frontend (In separate terminal)
```bash
cd SmartShopAI
expo start
```

---

## Test Scenarios

### Test 1: User Authentication & Wishlist Creation ✅

**Objective**: Verify OTP login creates default wishlist

**Steps**:
1. Open app (press 'i' for iOS simulator or 'a' for Android)
2. Enter email: `test@example.com`
3. Click "Send OTP"
4. Check backend logs for OTP (in dev mode, logged to console)
5. Enter OTP in app
6. Verify user is logged in

**Backend Verification**:
```bash
# Check if user was created in database
curl -X GET "http://localhost:8000/api/dashboard/USER_ID" \
  -H "Authorization: Bearer USER_ID"
```

**Expected**:
- ✅ User created in `users` table
- ✅ Default wishlist created in `wishlists` table with `is_default = true`
- ✅ User_id token stored in AsyncStorage on frontend

---

### Test 2: Add Product to Wishlist ✅

**Objective**: Verify product can be added to wishlist

**Steps**:
1. After login, tap "Explore" tab
2. Search for a product (e.g., "iPhone")
3. Tap "Add to Wishlist" or "Set Price Alert"
4. Enter target price (optional)
5. Click "Set Price Alert"

**Frontend Logs** (Expo):
```
📡 POST /api/wishlist/add with body: {"product_id": "...", "target_price": 29999}
✅ /api/wishlist/add response: {"success": true, "message": "Added to wishlist"}
```

**Backend Logs** (main.py):
```
📌 Adding product abc123 to wishlist for user xyz789
⚠️ Default wishlist not found for xyz789, creating...
✅ Product abc123 added to wishlist
```

**Expected**:
- ✅ Success alert on frontend
- ✅ Entry in `wishlist_items` table
- ✅ Link to correct `wishlist_id` and `product_id`
- ✅ `target_price` saved if provided

---

### Test 3: View Wishlist ✅

**Objective**: Verify wishlist items are displayed

**Steps**:
1. After adding product, tap "Wishlist" tab
2. Observe product card appears

**Frontend Logs**:
```
📋 Fetching wishlist...
📡 GET /api/wishlist
✅ Found 1 items in wishlist
```

**Backend Logs**:
```
📋 Fetching wishlist for user xyz789
✅ Found 1 items in wishlist
```

**Database Query** (Supabase SQL):
```sql
SELECT wi.*, p.name, p.price
FROM wishlist_items wi
JOIN wishlists w ON wi.wishlist_id = w.id
JOIN products p ON wi.product_id = p.id
WHERE w.user_id = 'xyz789' AND w.is_default = true;
```

**Expected**:
- ✅ Product card displays with name, price, platform
- ✅ Product name matches what was searched
- ✅ Price displays correctly
- ✅ Remove button is clickable

---

### Test 4: Remove from Wishlist ✅

**Objective**: Verify product can be removed

**Steps**:
1. From Wishlist tab, swipe or tap "Remove" on product
2. Confirm removal

**Expected**:
- ✅ Item removed from list immediately (frontend optimistic update)
- ✅ Entry deleted from `wishlist_items` table
- ✅ List updates to show empty state if last item

---

### Test 5: Scheduler Running ✅

**Objective**: Verify background scheduler is active

**Backend Logs** (watch for):
```
🚀 Starting APScheduler for background jobs...
✅ APScheduler started successfully

# Every 5 minutes in dev mode:
✅ Scheduler test job running (5 min interval)

# Every 6 hours in production:
🔍 Starting price alert check...
```

**Manual Trigger** (for testing):
```python
# Add this to a test endpoint to manually trigger
from utils.scheduler import get_scheduler

scheduler = get_scheduler()
# Manually call run_once on the scheduler
```

**Expected**:
- ✅ Scheduler logs appear in backend console
- ✅ No errors during job execution
- ✅ Jobs run at configured intervals

---

### Test 6: Price Monitoring (Manual Test) ✅

**Objective**: Verify price alerts trigger notifications

**Setup**:
1. Add product to wishlist with target price: ₹20,000
2. Current price in DB: ₹25,000

**Manual Test Steps**:
```sql
-- Update product price in Supabase
UPDATE product_prices
SET price = 19999
WHERE product_id = 'your_product_id'
AND platform_id = 'your_platform_id';

-- Wait 5 minutes (dev mode) for scheduler to run
-- Check logs and email
```

**Expected**:
- ✅ Backend logs show price drop detected
- ✅ Email sent to user's email address
- ✅ WhatsApp notification sent (if number configured)
- ✅ `price_alerts.notification_sent = true`

**Email Test**:
```
To: user@example.com
Subject: 🎉 Price Drop Alert: iPhone 15 is now ₹19,999!

[Formatted HTML email with:
- Product name
- Old price (₹25,000)
- New price (₹19,999)
- Percentage drop (20%)
- "View Product" button]
```

---

## API Testing with curl

### Request OTP
```bash
curl -X POST "http://localhost:8000/api/auth/request-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Response
{
  "success": true,
  "message": "OTP sent to your email!"
}
```

### Verify OTP
```bash
curl -X POST "http://localhost:8000/api/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "otp": "123456"
  }'

# Response
{
  "success": true,
  "user_id": "xyz789",
  "email": "test@example.com"
}
```

### Add to Wishlist
```bash
curl -X POST "http://localhost:8000/api/wishlist/add" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xyz789" \
  -d '{
    "product_id": "prod123",
    "target_price": 29999
  }'

# Response
{
  "success": true,
  "message": "Added to wishlist",
  "item": {
    "id": "item123",
    "product_id": "prod123",
    "target_price": 29999
  }
}
```

### Get Wishlist
```bash
curl -X GET "http://localhost:8000/api/wishlist" \
  -H "Authorization: Bearer xyz789"

# Response
{
  "wishlist_id": "wl123",
  "items": [
    {
      "id": "item123",
      "product_id": "prod123",
      "target_price": 29999,
      "added_at": "2026-05-18T10:30:00Z",
      "products": {
        "name": "iPhone 15",
        "price": 25000,
        "url": "https://amazon.in/iPhone-15",
        "platform": "Amazon"
      }
    }
  ]
}
```

### Remove from Wishlist
```bash
curl -X DELETE "http://localhost:8000/api/wishlist-items/item123" \
  -H "Authorization: Bearer xyz789"

# Response
{
  "success": true,
  "message": "Removed from wishlist"
}
```

---

## Troubleshooting

### Issue: "401 Unauthorized"
**Cause**: Missing or invalid Authorization header
**Solution**: 
1. Verify token from AsyncStorage: `await AsyncStorage.getItem('user_id')`
2. Pass as: `Authorization: Bearer <user_id>`
3. Check if OTP verification succeeded

### Issue: "Wishlist not found"
**Cause**: Default wishlist not created on OTP verification
**Solution**:
1. Check `utils/auth.py` line with wishlist creation
2. Verify Supabase `wishlists` table exists
3. Check database error logs

### Issue: "Scheduler not starting"
**Cause**: APScheduler not installed or import error
**Solution**:
```bash
pip install apscheduler>=3.10.0
pip install -r requirements.txt  # Reinstall all deps
python -c "from apscheduler.schedulers.background import BackgroundScheduler; print('✅ APScheduler OK')"
```

### Issue: "No notification sent"
**Cause**: Scheduler not running or email not configured
**Solution**:
1. Check backend logs for "Scheduler test job running"
2. Verify EMAIL_ADDRESS and EMAIL_PASSWORD in .env
3. Check price is actually below target_price
4. Wait for scheduler interval (5 min dev, 6 hours prod)

---

## Performance Baseline

### Expected Response Times
- POST /api/wishlist/add: 200-500ms
- GET /api/wishlist: 150-300ms
- DELETE /api/wishlist-items/{id}: 200-400ms

### Database Performance
- Query wishlists by user: < 10ms (indexed)
- Query wishlist_items: < 20ms (indexed)
- Scheduler job execution: 1-5 seconds

---

## Monitoring

### View Backend Logs
```bash
# Follow logs in real-time
tail -f logs/app.log

# Or in Python:
python -c "import logging; logging.basicConfig(level=logging.DEBUG); print('Logs shown here')"
```

### View Frontend Logs (Expo)
```
In Expo app, shake device or press 'm' to open menu → View logs
```

### Database Monitoring (Supabase)
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to Database → Query Editor
4. Run monitoring queries

---

## Success Criteria

Phase 1 is working correctly when:

- ✅ User can log in with OTP
- ✅ Default wishlist created automatically
- ✅ Product can be added to wishlist
- ✅ Products display in wishlist tab
- ✅ Products can be removed from wishlist
- ✅ Scheduler runs without errors
- ✅ Price monitoring job executes
- ✅ Notifications (email/WhatsApp) sent on price drop
- ✅ No error messages in logs
- ✅ All database entries correct

When all criteria met → **PHASE 1 COMPLETE ✅**
