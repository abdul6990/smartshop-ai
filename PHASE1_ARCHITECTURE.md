# Phase 1 - Architecture Diagram & Component Connections

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER DEVICE (Frontend)                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       React Native App (Expo)                         │   │
│  │                                                                       │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│  │  │  Login Screen    │  │  Explore Tab     │  │  Wishlist Tab    │  │   │
│  │  │  (login.tsx)     │  │  (explore.tsx)   │  │  (wishlist.tsx)  │  │   │
│  │  │                  │  │                  │  │                  │  │   │
│  │  │ • Enter email    │  │ • Search product │  │ • Display items  │  │   │
│  │  │ • Enter OTP      │  │ • View details   │  │ • Remove item    │  │   │
│  │  │ • Store token    │  │ • Add to wishlist│  │ • Show chart     │  │   │
│  │  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │   │
│  │           │                     │                     │             │   │
│  │           └─────────────────────┼─────────────────────┘             │   │
│  │                                 │                                   │   │
│  │                    ┌────────────▼─────────────┐                    │   │
│  │                    │   utils/api.ts           │                    │   │
│  │                    │                          │                    │   │
│  │                    │ • authAPI                │                    │   │
│  │                    │ • wishlistAPI            │                    │   │
│  │                    │ • alertsAPI              │                    │   │
│  │                    │ • productsAPI            │                    │   │
│  │                    │                          │                    │   │
│  │                    │ Features:                │                    │   │
│  │                    │ ✓ Bearer token (Bearer)  │                    │   │
│  │                    │ ✓ AsyncStorage read      │                    │   │
│  │                    │ ✓ Error handling         │                    │   │
│  │                    │ ✓ 401 redirect           │                    │   │
│  │                    └────────────┬─────────────┘                    │   │
│  │                                 │                                   │   │
│  │                    ┌────────────▼─────────────┐                    │   │
│  │                    │  AsyncStorage            │                    │   │
│  │                    │                          │                    │   │
│  │                    │ • user_id (token)        │                    │   │
│  │                    │ • preferences            │                    │   │
│  │                    │ • cache data             │                    │   │
│  │                    └──────────────────────────┘                    │   │
│  │                                                                       │   │
│  └───────────────────────────────────┬───────────────────────────────────┘   │
│                                      │                                        │
│                                      │ HTTP/HTTPS                             │
│                                      │                                        │
└──────────────────────────────────────┼────────────────────────────────────────┘
                                       │
                                       ▼
        ┌──────────────────────────────────────────────────────────┐
        │            FastAPI Backend Server (Python)               │
        │            http://localhost:8000                          │
        │                                                           │
        │  ┌──────────────────────────────────────────────────┐   │
        │  │              API Endpoints                        │   │
        │  │                                                  │   │
        │  │  POST   /api/auth/request-otp                   │   │
        │  │  POST   /api/auth/verify-otp                    │   │
        │  │  POST   /api/wishlist/add                       │   │
        │  │  GET    /api/wishlist                           │   │
        │  │  DELETE /api/wishlist-items/{item_id}           │   │
        │  │                                                  │   │
        │  └────────┬─────────────────────────────┬──────────┘   │
        │           │                             │                │
        │           ▼                             ▼                │
        │  ┌──────────────────┐      ┌──────────────────────┐    │
        │  │  main.py         │      │  Dependency Inject   │    │
        │  │                  │      │  get_current_user()  │    │
        │  │ • CORS configured│      │                      │    │
        │  │ • Auth checking  │      │ • Extract user_id    │    │
        │  │ • Startup events │      │   from Bearer token  │    │
        │  │ • Shutdown events│      │ • Validate user      │    │
        │  └─────────┬────────┘      └──────────┬───────────┘    │
        │            │                          │                  │
        │            └──────────────┬───────────┘                  │
        │                           │                              │
        │                 ┌─────────▼─────────┐                   │
        │                 │  Service Layer    │                   │
        │                 │                   │                   │
        │                 │ ┌───────────────┐ │                   │
        │                 │ │   auth.py     │ │                   │
        │                 │ │               │ │                   │
        │                 │ │ verify_otp()  │ │                   │
        │                 │ │ → creates     │ │                   │
        │                 │ │   default     │ │                   │
        │                 │ │   wishlist    │ │                   │
        │                 │ └───────────────┘ │                   │
        │                 │                   │                   │
        │                 │ ┌───────────────┐ │                   │
        │                 │ │wishlist_svc.py│ │                   │
        │                 │ │               │ │                   │
        │                 │ │add_to_wishlist│ │                   │
        │                 │ │get_wishlist...|  │                   │
        │                 │ └───────────────┘ │                   │
        │                 │                   │                   │
        │                 │ ┌───────────────┐ │                   │
        │                 │ │ scheduler.py  │ │                   │
        │                 │ │               │ │                   │
        │                 │ │ APScheduler   │ │                   │
        │                 │ │ • start()     │ │                   │
        │                 │ │ • stop()      │ │                   │
        │                 │ │ • run_once()  │ │                   │
        │                 │ └───────────────┘ │                   │
        │                 └─────────┬─────────┘                   │
        │                           │                              │
        │         ┌─────────────────┼──────────────────┐           │
        │         │                 │                  │           │
        │         ▼                 ▼                  ▼           │
        │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
        │   │ Supabase     │  │ Email (Gmail)│  │ WhatsApp     │ │
        │   │ Client       │  │ SMTP         │  │ (Twilio)     │ │
        │   └──────────────┘  └──────────────┘  └──────────────┘ │
        │                                                           │
        │  ┌────────────────────────────────────────────────────┐  │
        │  │          Background Scheduler (APScheduler)        │  │
        │  │                                                    │  │
        │  │  ┌──────────────────────────────────────────────┐ │  │
        │  │  │  Job 1: check_price_alerts                  │ │  │
        │  │  │  Interval: Every 6 hours (prod)             │ │  │
        │  │  │           Every 5 minutes (dev)             │ │  │
        │  │  │                                              │ │  │
        │  │  │  Actions:                                    │ │  │
        │  │  │  1. Query active price alerts               │ │  │
        │  │  │  2. Compare current_price vs alert_price    │ │  │
        │  │  │  3. If price dropped:                        │ │  │
        │  │  │     • Send email notification               │ │  │
        │  │  │     • Send WhatsApp notification            │ │  │
        │  │  │     • Update last_triggered_at              │ │  │
        │  │  └──────────────────────────────────────────────┘ │  │
        │  │                                                    │  │
        │  └────────────────────────────────────────────────────┘  │
        │                                                           │
        └───────────────────────┬─────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────────┐
        │   Supabase PostgreSQL Database                │
        │   https://vguauwgcsfvjidglmjxs.supabase.co   │
        │                                               │
        │   Tables:                                     │
        │   ┌─────────────────────────────────────┐    │
        │   │ users                               │    │
        │   │ • id (UUID, PK)                    │    │
        │   │ • email (UNIQUE)                   │    │
        │   │ • is_verified (BOOLEAN)            │    │
        │   └─────────────────────────────────────┘    │
        │                                               │
        │   ┌─────────────────────────────────────┐    │
        │   │ wishlists                           │    │
        │   │ • id (UUID, PK)                    │    │
        │   │ • user_id (FK → users)             │    │
        │   │ • is_default (BOOLEAN)             │    │
        │   │ • name, description                │    │
        │   └─────────────────────────────────────┘    │
        │                                               │
        │   ┌─────────────────────────────────────┐    │
        │   │ wishlist_items                      │    │
        │   │ • id (UUID, PK)                    │    │
        │   │ • wishlist_id (FK → wishlists)    │    │
        │   │ • product_id (FK → products)      │    │
        │   │ • target_price (DECIMAL)          │    │
        │   │ • price_when_added (DECIMAL)      │    │
        │   └─────────────────────────────────────┘    │
        │                                               │
        │   ┌─────────────────────────────────────┐    │
        │   │ price_alerts                        │    │
        │   │ • id (UUID, PK)                    │    │
        │   │ • user_id (FK → users)             │    │
        │   │ • product_id (FK → products)      │    │
        │   │ • alert_price (DECIMAL)           │    │
        │   │ • notification_sent (BOOLEAN)     │    │
        │   │ • is_active (BOOLEAN)             │    │
        │   └─────────────────────────────────────┘    │
        │                                               │
        │   ┌─────────────────────────────────────┐    │
        │   │ products                            │    │
        │   │ • id (UUID, PK)                    │    │
        │   │ • name (VARCHAR)                   │    │
        │   │ • brand, model, color              │    │
        │   │ • category_id (FK → categories)   │    │
        │   └─────────────────────────────────────┘    │
        │                                               │
        │   ┌─────────────────────────────────────┐    │
        │   │ product_prices                      │    │
        │   │ • id (UUID, PK)                    │    │
        │   │ • product_id (FK → products)      │    │
        │   │ • platform_id (FK → platforms)    │    │
        │   │ • price (DECIMAL)                 │    │
        │   │ • last_checked (TIMESTAMP)        │    │
        │   └─────────────────────────────────────┘    │
        │                                               │
        └───────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Flow 1: User Login + Default Wishlist Creation

```
┌─────────────┐
│ User enters │
│ email & OTP │
└──────┬──────┘
       │
       ▼
┌────────────────────────────┐
│ Frontend: authAPI.verifyOTP│
│ POST /api/auth/verify-otp  │
└──────┬─────────────────────┘
       │ Request:
       │ {email, otp}
       │
       ▼
┌──────────────────────────┐
│ Backend: verify_otp()    │
│                          │
│ 1. Validate OTP          │
│ 2. Call verify_otp()     │
│    from utils/auth.py    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ utils/auth.py: verify_otp()      │
│                                  │
│ 1. Check OTP expiry              │
│ 2. Call _ensure_user_exists()    │
│ 3. User created/retrieved        │
│    (saves to users table)         │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Create Default Wishlist          │
│ (NEW: Added in Phase 1)          │
│                                  │
│ SELECT wishlists                 │
│ WHERE user_id = @user_id         │
│   AND is_default = true          │
│                                  │
│ If NOT exists:                   │
│   INSERT into wishlists          │
│   (user_id, is_default=true)     │
└──────┬───────────────────────────┘
       │ Database updated
       │
       ▼
┌──────────────────────────┐
│ Response: { success,     │
│            user_id,      │
│            email }       │
└──────┬───────────────────┘
       │
       ▼
┌────────────────────────────────┐
│ Frontend:                      │
│ 1. Store user_id in AsyncStore │
│ 2. Navigate to home            │
│ 3. Show welcome message        │
└────────────────────────────────┘
```

### Flow 2: Add Product to Wishlist

```
┌──────────────────────────┐
│ User taps "Add to List"  │
│ Enters target price      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Frontend: track.tsx              │
│ handleSetAlert()                 │
│                                  │
│ wishlistAPI.addProduct(          │
│   productId,                     │
│   targetPrice                    │
│ )                                │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ API Client: utils/api.ts         │
│                                  │
│ 1. Get user_id from AsyncStorage │
│ 2. Create Authorization header   │
│    Bearer: user_id               │
│ 3. POST /api/wishlist/add        │
│    Body: {product_id, target...} │
└──────┬───────────────────────────┘
       │ HTTP POST request
       │
       ▼
┌──────────────────────────────────┐
│ Backend: main.py                 │
│ @app.post("/api/wishlist/add")   │
│                                  │
│ 1. Extract user_id from header   │
│ 2. Get user's default wishlist   │
│    SELECT wishlists              │
│    WHERE user_id = @user_id      │
│      AND is_default = true       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ utils/wishlist_service.py        │
│ add_to_wishlist()                │
│                                  │
│ INSERT into wishlist_items       │
│ (wishlist_id, product_id,        │
│  target_price, price_when_added) │
└──────┬───────────────────────────┘
       │ Database updated
       │
       ▼
┌──────────────────────────────────┐
│ Response: {                      │
│   success: true,                 │
│   message: "Added to wishlist",  │
│   item: {...}                    │
│ }                                │
└──────┬───────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│ Frontend:                      │
│ 1. Show success alert          │
│ 2. Navigate back               │
│ 3. Refresh wishlist (optional) │
└────────────────────────────────┘
```

### Flow 3: Display Wishlist

```
┌──────────────────────────┐
│ User opens Wishlist tab  │
│ wishlist.tsx mount()     │
└──────┬───────────────────┘
       │ useEffect runs
       │
       ▼
┌──────────────────────────────────┐
│ Frontend: wishlist.tsx           │
│ fetchWishlist()                  │
│                                  │
│ wishlistAPI.getWishlist()        │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ API Client: utils/api.ts         │
│                                  │
│ 1. Get user_id from AsyncStorage │
│ 2. Create Authorization header   │
│ 3. GET /api/wishlist             │
└──────┬───────────────────────────┘
       │ HTTP GET request
       │
       ▼
┌──────────────────────────────────┐
│ Backend: main.py                 │
│ @app.get("/api/wishlist")        │
│                                  │
│ 1. Extract user_id from header   │
│ 2. Get user's default wishlist   │
│    SELECT wishlists              │
│    WHERE user_id = @user_id      │
│      AND is_default = true       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Query wishlist items with        │
│ product details                  │
│                                  │
│ SELECT wi.*, p.name, p.price,    │
│        p.url, p.platform         │
│ FROM wishlist_items wi           │
│ JOIN products p                  │
│   ON wi.product_id = p.id        │
│ WHERE wi.wishlist_id = @wl_id    │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Response: {                      │
│   wishlist_id: "123",            │
│   items: [                       │
│     {                            │
│       id: "item1",               │
│       product_id: "prod1",       │
│       target_price: 29999,       │
│       products: {                │
│         name: "iPhone",          │
│         price: 25000,            │
│         url: "...",              │
│         platform: "Amazon"       │
│       }                          │
│     },                           │
│     ...more items                │
│   ]                              │
│ }                                │
└──────┬───────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│ Frontend: wishlist.tsx          │
│                                │
│ 1. Format response data        │
│ 2. Render FlatList with items  │
│ 3. Show product cards          │
│ 4. Display prices & buttons    │
└────────────────────────────────┘
```

### Flow 4: Price Monitoring (Background)

```
┌──────────────────────────────┐
│ App Startup                  │
│ FastAPI @app.on_event()      │
└──────┬───────────────────────┘
       │ startup event
       │
       ▼
┌──────────────────────────────────┐
│ main.py: startup_event()         │
│                                  │
│ from utils.scheduler import      │
│   start_background_scheduler     │
│                                  │
│ start_background_scheduler()     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ scheduler.py:                    │
│ start_background_scheduler()     │
│                                  │
│ 1. Create BackgroundScheduler    │
│ 2. Register check_price_alerts   │
│    job (Interval: 6 hours)       │
│ 3. Scheduler.start()             │
└──────┬───────────────────────────┘
       │ Scheduler running
       │
       ▼
┌──────────────────────────────────┐
│ Trigger: Every 6 hours           │
│ (Every 5 min in dev mode)        │
│                                  │
│ PriceScheduler.run_once()        │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Query active price alerts:       │
│                                  │
│ SELECT pa.* FROM price_alerts pa │
│ JOIN wishlist_items wi           │
│ WHERE pa.is_active = true        │
│   AND pa.wishlist_item_id =wi.id │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ For each alert:                  │
│                                  │
│ 1. Get current product price     │
│ 2. Compare with alert_price      │
│                                  │
│ if current_price <=              │
│    alert_price:                  │
│   → ALERT TRIGGERED!             │
└──────┬───────────────────────────┘
       │ Price dropped
       │
       ▼
┌──────────────────────────────────┐
│ Send Notifications:              │
│                                  │
│ 1. Get user email                │
│ 2. Send email via Gmail SMTP     │
│    Subject: "🎉 Price Alert!"    │
│    Body: Formatted HTML          │
│                                  │
│ 3. Get WhatsApp number           │
│ 4. Send WhatsApp via Twilio      │
│    Message: Price alert text     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Update Database:                 │
│                                  │
│ UPDATE price_alerts              │
│ SET notification_sent = true,    │
│     last_triggered_at = NOW()    │
│ WHERE id = @alert_id             │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Log completion:                  │
│ "✅ Price alert triggered for    │
│  iPhone 15 at ₹19,999"           │
│                                  │
│ Wait 6 hours for next cycle      │
└──────────────────────────────────┘
```

---

## Component Dependency Map

```
Frontend (React Native)
│
├── SmartShopAI/app/track.tsx
│   ├── imports: wishlistAPI from utils/api.ts
│   ├── imports: getUserId from utils/auth.ts
│   └── calls: wishlistAPI.addProduct()
│
├── SmartShopAI/app/(tabs)/wishlist.tsx
│   ├── imports: wishlistAPI from utils/api.ts
│   ├── imports: getUserId from utils/auth.ts
│   └── calls: wishlistAPI.getWishlist()
│
└── SmartShopAI/utils/api.ts ⭐ CREATED
    ├── exports: wishlistAPI
    ├── exports: alertsAPI
    ├── exports: productsAPI
    ├── exports: authAPI
    ├── uses: AsyncStorage for token
    └── handles: Authorization headers

Backend (Python)
│
├── main.py
│   ├── imports: app from FastAPI
│   ├── imports: scheduler from utils/scheduler
│   ├── @app.post("/api/wishlist/add")
│   │   └── calls: add_to_wishlist() from utils/wishlist_service
│   ├── @app.get("/api/wishlist")
│   │   └── calls: get_wishlist_with_items() from utils/wishlist_service
│   ├── @app.post("/api/auth/verify-otp")
│   │   └── calls: verify_otp() from utils/auth
│   ├── @app.on_event("startup")
│   │   └── calls: start_background_scheduler()
│   └── @app.on_event("shutdown")
│       └── calls: stop_background_scheduler()
│
├── utils/auth.py ⭐ MODIFIED
│   ├── verify_otp(): Verify OTP
│   ├── _ensure_user_exists(): Create user
│   └── NEW: Create default wishlist on OTP verification
│
├── utils/scheduler.py ⭐ MODIFIED
│   ├── start_background_scheduler(): Start APScheduler
│   ├── stop_background_scheduler(): Stop APScheduler
│   ├── PriceScheduler.run_once(): Monitor prices
│   └── Triggers notifications on price drop
│
├── utils/wishlist_service.py
│   ├── add_to_wishlist(): Add product to wishlist
│   └── get_wishlist_with_items(): Fetch wishlist items
│
└── utils/supabase_client.py
    └── db: Supabase client instance

Database (Supabase)
│
├── users (id, email, is_verified)
│   ├── wishlists (user_id, is_default) ⭐
│   │   └── wishlist_items (product_id, target_price) ⭐
│   │
│   └── price_alerts (product_id, alert_price) ⭐
│
└── products (id, name, price, brand)
    └── product_prices (product_id, platform_id, price)

Services
│
├── Email (Gmail SMTP)
│   └── Sends price drop notifications
│
├── WhatsApp (Twilio)
│   └── Sends price drop notifications
│
└── Scheduler (APScheduler)
    └── Runs price monitoring every 6 hours
```

---

## Key Integration Points ✅

### 1. **Authentication to Wishlist** ✅
```
Frontend Login
  → OTP Verification
    → Backend creates user + default wishlist
      → User_id stored in AsyncStorage
        → Used as Bearer token in all future API calls
```

### 2. **Frontend to Backend** ✅
```
track.tsx
  → wishlistAPI.addProduct()
    → Authorization: Bearer {user_id}
      → POST /api/wishlist/add
        → Backend extracts user_id from header
          → Gets user's default wishlist
            → Adds product to wishlist_items
              → Returns success response
```

### 3. **Wishlist Display** ✅
```
wishlist.tsx
  → wishlistAPI.getWishlist()
    → Authorization: Bearer {user_id}
      → GET /api/wishlist
        → Queries wishlists + wishlist_items + products
          → Returns formatted items
            → Rendered in FlatList
```

### 4. **Background Monitoring** ✅
```
App Startup
  → @app.on_event("startup")
    → start_background_scheduler()
      → APScheduler registers job
        → Every 6 hours: PriceScheduler.run_once()
          → Queries price_alerts
            → Compares prices
              → Sends notifications if dropped
```

---

## Verification Results

| Component | Status | Details |
|-----------|--------|---------|
| Frontend API Client | ✅ | SmartShopAI/utils/api.ts created |
| Track Screen Integration | ✅ | Imports wishlistAPI, calls addProduct() |
| Wishlist Tab Integration | ✅ | Imports wishlistAPI, calls getWishlist() |
| Backend Endpoints | ✅ | 5 endpoints for wishlist CRUD |
| Auth Wishlist Creation | ✅ | Default wishlist created on OTP verify |
| Scheduler Integration | ✅ | Startup/shutdown events configured |
| Database Tables | ✅ | All required tables exist and are accessible |
| Error Handling | ✅ | All layers have proper error handling |
| Data Validation | ✅ | Pydantic models for request/response |

**PHASE 1 IS VERIFIED AND READY FOR TESTING ✅**
