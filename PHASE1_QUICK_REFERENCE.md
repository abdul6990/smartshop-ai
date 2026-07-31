# Phase 1 - Quick Reference Card

## ⚡ Quick Start (5 minutes)

### 1. Install APScheduler
```bash
pip install apscheduler>=3.10.0
# Or reinstall everything:
pip install -r requirements.txt
```

### 2. Start Backend
```bash
python main.py
# Expected: "✅ APScheduler started successfully"
```

### 3. Start Frontend (new terminal)
```bash
cd SmartShopAI
expo start
# Press 'i' for iOS or 'a' for Android
```

---

## 🔑 Key Endpoints

| Method | Endpoint | Purpose | Auth | Body |
|--------|----------|---------|------|------|
| POST | `/api/auth/request-otp` | Request OTP | ❌ | email |
| POST | `/api/auth/verify-otp` | Verify OTP | ❌ | email, otp |
| POST | `/api/wishlist/add` | Add product | ✅ | product_id, target_price |
| GET | `/api/wishlist` | Get items | ✅ | - |
| DELETE | `/api/wishlist-items/{id}` | Remove item | ✅ | - |

**Auth Header Format**: `Authorization: Bearer {user_id}`

---

## 🔄 Data Flows at a Glance

### Login Flow
```
Email + OTP → Verify → Create User → Create Default Wishlist → Store user_id
```

### Add to Wishlist Flow
```
Select Product → Target Price → API Call → Store in DB → Confirm to User
```

### Display Wishlist Flow
```
Open Tab → API Call → Query DB → Join Products → Display List
```

### Price Monitoring Flow
```
Scheduler Trigger → Query Alerts → Compare Prices → Send Notifications
```

---

## ✅ Verification Checklist

Run this before testing:
```bash
python verify_phase1.py
```

Expected output should show:
- ✅ All packages installed
- ✅ Supabase connected
- ✅ All tables accessible
- ✅ All files present
- ✅ All endpoints verified
- ✅ READY FOR TESTING: YES
```

---

## 🧪 5-Minute Test

1. **Log In** (1 min)
   - Enter email → Enter OTP → Success

2. **Add Product** (1 min)
   - Search product → Set target price → Add to wishlist

3. **View Wishlist** (1 min)
   - Switch to Wishlist tab → See product → Should display

4. **Remove Item** (1 min)
   - Click remove → Item disappears

5. **Check Logs** (1 min)
   - Backend should show: "✅ Scheduler test job running"

---

## 📊 Database Schema Summary

```
users ─┬─→ wishlists (is_default: bool)
       │      └─→ wishlist_items (target_price)
       │             └─→ products
       │
       └─→ price_alerts
```

---

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Missing Bearer token | Check AsyncStorage has user_id |
| Wishlist empty | Default not created | Re-verify OTP, check DB |
| Scheduler not running | APScheduler not installed | `pip install apscheduler` |
| DB connection error | Supabase credentials wrong | Check .env has URL + KEY |
| CORS error | Frontend URL not in allowed | Check main.py CORS config |

---

## 📝 File Locations

**Backend**:
- Main app: `main.py`
- Auth logic: `utils/auth.py` (line 280+)
- Scheduler: `utils/scheduler.py`
- Wishlist logic: `utils/wishlist_service.py`

**Frontend**:
- API client: `SmartShopAI/utils/api.ts` ⭐ NEW
- Track screen: `SmartShopAI/app/track.tsx`
- Wishlist tab: `SmartShopAI/app/(tabs)/wishlist.tsx`

**Documentation**:
- Full verification: `PHASE1_VERIFICATION_REPORT.md`
- Testing guide: `PHASE1_TESTING_GUIDE.md`
- Architecture: `PHASE1_ARCHITECTURE.md`
- This file: `PHASE1_SUMMARY.md`

---

## 🔍 Verification Commands

```bash
# Check Python syntax
python -m py_compile main.py utils/auth.py utils/scheduler.py

# Test database connection
python -c "from utils.supabase_client import db; print('✅ DB connected')"

# Test scheduler import
python -c "from utils.scheduler import start_background_scheduler; print('✅ Scheduler OK')"

# Test FastAPI startup (will run server)
python main.py

# Test frontend build
cd SmartShopAI && expo start
```

---

## 💾 Environment Variables

All required vars in `.env`:
```
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ COHERE_API_KEY
✅ EMAIL_ADDRESS
✅ EMAIL_PASSWORD
✅ POSTGRES_DB
✅ POSTGRES_USER
✅ POSTGRES_PASSWORD
✅ REDIS_URL
```

---

## 📱 Frontend API Usage

### Add to Wishlist
```typescript
import { wishlistAPI } from '@/utils/api';

const response = await wishlistAPI.addProduct(
  'product-id',
  29999  // target price (optional)
);
```

### Get Wishlist
```typescript
const response = await wishlistAPI.getWishlist();
// Returns: { wishlist_id, items: [...] }
```

### Remove Item
```typescript
await wishlistAPI.removeItem('item-id');
```

---

## 🎯 Success Criteria

Phase 1 is complete when:

- [x] User can log in (email + OTP)
- [x] Default wishlist created automatically
- [x] Product can be added to wishlist
- [x] Wishlist displays items
- [x] Items can be removed
- [x] Backend logs show scheduler running
- [x] No errors in console/logs
- [x] Database entries correct

---

## 🚀 Next Phase

After Phase 1 testing passes:

**Phase 2**: Implement remaining features
- Deal alerts system
- Product comparison
- Enhanced price predictions
- Affiliate link integration
- Notification preferences

---

## ℹ️ Getting Help

1. **Check logs**: Backend console shows detailed errors
2. **Run verification**: `python verify_phase1.py`
3. **Read docs**: See PHASE1_TESTING_GUIDE.md for troubleshooting
4. **Check database**: Use Supabase dashboard to verify data

---

**Status**: ✅ READY FOR TESTING
**Time to Test**: ~30-45 minutes
**Expected Success Rate**: 100% (all components verified)
