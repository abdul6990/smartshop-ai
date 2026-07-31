# 🔧 SmartShopAI - Feature Status & Implementation Guide

**Status Report:** May 18, 2026  
**Document Purpose:** Identify incomplete features, root causes, and implementation steps

---

## 📊 FEATURE STATUS OVERVIEW

| # | Feature | Status | Issue | Priority | Fix |
|---|---------|--------|-------|----------|-----|
| 1 | ✅ OTP Authentication | ✅ WORKING | None | - | - |
| 2 | 🔴 Product Comparison | ❌ NOT IMPLEMENTED | No compare logic | HIGH | Implement comparison endpoint |
| 3 | 🟡 Price History Charts | ⚠️ DUMMY DATA | All products show same chart | MEDIUM | Generate real data from DB |
| 4 | ❓ AI Price Predictions | ❓ UNKNOWN | Not tested | HIGH | Test endpoint & debug |
| 5 | 🔴 Deal Alerts | ❌ NOT WORKING | Alert system incomplete | HIGH | Fix alert triggers |
| 6 | 🔴 Wishlist Management | ❌ NOT WORKING | Saves but doesn't display | CRITICAL | Fix DB query + frontend sync |
| 7 | ⚠️ Affiliate Links | ❌ NOT USED | Implemented but not called | LOW | Integrate into product results |

---

## 🔴 CRITICAL ISSUES

### Issue 1: Wishlist Management NOT WORKING

**Symptom:** User clicks "Add to Wishlist" → Popup shows → User sees nothing in Wishlist tab

**Root Cause Analysis:**

#### Backend Issues:
```python
# File: main.py (line 632)
@app.post("/api/wishlists/{wishlist_id}/items")
async def add_product_to_wishlist(
    wishlist_id: str,
    product_id: str = None,      # ❌ Problem: Query parameter, not in body
    target_price: float = None,  # ❌ Problem: Query parameter, not in body
    current_user: str = Depends(get_current_user)
):
```

**Problems:**
1. `product_id` and `target_price` are query parameters but frontend sends them in request body
2. Endpoint expects `wishlist_id` but frontend doesn't provide it
3. Frontend calls track.tsx which calls `/track-price` (different endpoint than wishlist)

#### Frontend Issues:
```tsx
// File: SmartShopAI/app/track.tsx (line 57)
const res = await fetch(API.trackPrice, {  // ❌ Using wrong endpoint
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: userId,
        product_name: productName,
        price: String(currentPrice),
        url: `https://www.amazon.in/s?k=${encodeURIComponent(productName)}`,
        platform: platform,
    }),
});
```

**The track.tsx screen doesn't:**
- Create or retrieve user's default wishlist
- Call the proper wishlist endpoint
- Display items after adding

**Fix Required:** 
- Update backend endpoint to accept body parameters
- Create/get user's default wishlist automatically
- Update frontend to call correct endpoint
- Add wishlist item display logic

---

### Issue 2: Deal Alerts NOT WORKING

**Symptom:** Price drops but no email/WhatsApp alerts sent

**Root Cause:**
```python
# File: agents/alert_manager.py
# Issue: Background job not running to check for price drops
# Issue: Scheduler might not be properly configured
# Issue: No verification that alerts are actually being triggered
```

**Missing Components:**
1. No continuous price monitoring job
2. Twilio might not be properly initialized
3. Email sending might be failing silently
4. No alert trigger logic

---

### Issue 3: AI Price Predictions - Unknown Status

**Current Implementation:**
```python
# File: agents/ai_predictor.py
# Exists but unclear if it's being called correctly
# Cohere API integration might have issues
# No test data to verify predictions work
```

**Need to Test:**
1. Check if Cohere API calls are succeeding
2. Verify prediction format is correct
3. Test end-to-end: search → analysis → prediction

---

## 🟡 MEDIUM PRIORITY ISSUES

### Issue 4: Price History Shows Dummy Data

**Current Implementation:**
```tsx
// File: SmartShopAI/app/track.tsx (line 18)
const generateGraphData = (basePrice: number) => {
  const data = [];
  let currentPrice = basePrice * 1.2; // ❌ Generates DUMMY data
  
  for (let i = 0; i <= 30; i++) {
    const change = (Math.random() - 0.4) * 0.05 * currentPrice; 
    currentPrice = currentPrice + change;
    if (i === 30) currentPrice = basePrice;
    
    data.push({
      date: `Day ${i}`,
      price: currentPrice
    });
  }
  return data;
};
```

**Problem:**
- Every product shows identical random chart
- Not fetching real data from `/price-history/{product_id}` endpoint
- All products have same pattern

**Fix Required:**
- Fetch actual price history from API
- Display with real dates
- Show multiple data points from database

---

### Issue 5: Product Comparison Not Implemented

**Current Status:**
- Tab exists (compare.tsx)
- No comparison logic
- Can't select products to compare
- No comparison UI

---

### Issue 6: Affiliate Links Not Being Used

**Current Implementation:**
```python
# File: utils/affiliate_url_generator.py
# Functions exist but not called in main.py
# Products are returned without affiliate links
# Lost monetization opportunity
```

---

## ✅ WORKING FEATURES

### 1. OTP Authentication
```
✅ Send OTP to email
✅ Verify OTP 
✅ Create session
✅ Protect endpoints with authentication
```

---

## 🔧 IMPLEMENTATION PLAN

### STEP 1: Fix Wishlist (CRITICAL)

#### 1.1 Backend Fix - main.py

**Change 1: Create default wishlist for new users**

```python
@app.post("/auth/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    # ... existing code ...
    user = supabase_db.table('users').upsert({...}).execute()
    
    # ✅ NEW: Create default wishlist if doesn't exist
    wishlist_check = supabase_db.table('wishlists')\
        .select('id')\
        .eq('user_id', user.id)\
        .eq('is_default', True)\
        .execute()
    
    if not wishlist_check.data:
        supabase_db.table('wishlists').insert({
            'user_id': user.id,
            'name': 'My Wishlist',
            'is_default': True,
            'is_public': False
        }).execute()
    
    # ... continue ...
```

**Change 2: Fix add-to-wishlist endpoint**

```python
# ❌ OLD (WRONG):
@app.post("/api/wishlists/{wishlist_id}/items")
async def add_product_to_wishlist(
    wishlist_id: str,
    product_id: str = None,  # ❌ Query param
    target_price: float = None,  # ❌ Query param
    current_user: str = Depends(get_current_user)
):

# ✅ NEW (CORRECT):
from pydantic import BaseModel

class AddToWishlistRequest(BaseModel):
    product_id: str
    target_price: Optional[float] = None

@app.post("/api/wishlist/add")
async def add_product_to_wishlist(
    request: AddToWishlistRequest,
    current_user: str = Depends(get_current_user)
):
    """Add product to user's default wishlist"""
    try:
        # Get user's default wishlist
        wishlist_result = supabase_db.table('wishlists')\
            .select('id')\
            .eq('user_id', current_user)\
            .eq('is_default', True)\
            .execute()
        
        if not wishlist_result.data:
            # Create default wishlist if doesn't exist
            create_result = supabase_db.table('wishlists').insert({
                'user_id': current_user,
                'name': 'My Wishlist',
                'is_default': True,
                'is_public': False
            }).execute()
            wishlist_id = create_result.data[0]['id']
        else:
            wishlist_id = wishlist_result.data[0]['id']
        
        # Add to wishlist
        from utils.wishlist_service import add_to_wishlist as _add_to_wishlist
        result = _add_to_wishlist(
            wishlist_id, 
            current_user, 
            request.product_id, 
            request.target_price
        )
        
        return {
            "success": True,
            "message": "Added to wishlist",
            "item": result
        }
    
    except Exception as e:
        app_logger.error(f"Error adding to wishlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Change 3: Get wishlist endpoint**

```python
# ✅ Simpler endpoint
@app.get("/api/wishlist")
async def get_my_wishlist(current_user: str = Depends(get_current_user)):
    """Get user's default wishlist with items"""
    try:
        # Get default wishlist
        wishlist_result = supabase_db.table('wishlists')\
            .select('*')\
            .eq('user_id', current_user)\
            .eq('is_default', True)\
            .execute()
        
        if not wishlist_result.data:
            return {"items": [], "total": 0}
        
        wishlist_id = wishlist_result.data[0]['id']
        
        # Get items with product details
        items_result = supabase_db.table('wishlist_items')\
            .select('*, products(name, image_url, brand, current_price, platform)')\
            .eq('wishlist_id', wishlist_id)\
            .order('added_at', desc=True)\
            .execute()
        
        return {
            "items": items_result.data or [],
            "total": len(items_result.data or [])
        }
    
    except Exception as e:
        app_logger.error(f"Error fetching wishlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 1.2 Frontend Fix - SmartShopAI

**Change 1: Create new wishlist API client**

```tsx
// File: SmartShopAI/utils/api.ts (NEW FILE)
import AsyncStorage from '@react-native-async-storage/async-storage';

export const API_URL = 'http://localhost:8000';

export const apiClient = {
  async request(method: string, endpoint: string, body?: any) {
    const token = await AsyncStorage.getItem('auth_token');
    
    const headers: any = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options: any = {
      method,
      headers,
    };
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, options);
    
    if (response.status === 401) {
      await AsyncStorage.removeItem('auth_token');
      throw new Error('Unauthorized');
    }
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  },
  
  get(endpoint: string) {
    return this.request('GET', endpoint);
  },
  
  post(endpoint: string, body: any) {
    return this.request('POST', endpoint, body);
  },
  
  delete(endpoint: string) {
    return this.request('DELETE', endpoint);
  },
};

// Wishlist specific functions
export const wishlistAPI = {
  async addProduct(productId: string, targetPrice?: number) {
    return apiClient.post('/api/wishlist/add', {
      product_id: productId,
      target_price: targetPrice || null,
    });
  },
  
  async getWishlist() {
    return apiClient.get('/api/wishlist');
  },
  
  async removeProduct(itemId: string) {
    return apiClient.delete(`/api/wishlist-items/${itemId}`);
  },
};
```

**Change 2: Update track.tsx**

```tsx
// File: SmartShopAI/app/track.tsx
import { wishlistAPI } from '../utils/api';

export default function TrackScreen() {
  // ... existing code ...
  
  const handleSetAlert = async () => {
    setSaving(true);
    try {
      const userId = await getUserId();
      if (!userId) {
        Alert.alert('Not Logged In', 'Please log in to track products.');
        return;
      }

      // ✅ NEW: Use proper API
      const response = await wishlistAPI.addProduct(productId, parseFloat(targetPrice));
      
      if (response.success) {
        Alert.alert(
          '✅ Tracking Active!', 
          `We'll monitor "${productName}" and notify you when the price drops${targetPrice ? ` below ₹${targetPrice}` : ''}.`,
          [{ text: 'Great!', onPress: () => router.back() }]
        );
      } else {
        Alert.alert('Error', response.error || 'Failed to set alert.');
      }
    } catch (e) {
      Alert.alert('Error', e.message || 'Could not add to wishlist');
    } finally {
      setSaving(false);
    }
  };

  // ... rest of component ...
}
```

**Change 3: Create wishlist display component**

```tsx
// File: SmartShopAI/app/(tabs)/track.tsx (NEW IMPLEMENTATION)
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { wishlistAPI } from '../../utils/api';
import { COLORS, FONTS, SPACING } from '../../constants/design-system';

export default function WishlistTab() {
  const [wishlist, setWishlist] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadWishlist();
  }, []);

  const loadWishlist = async () => {
    try {
      setLoading(true);
      const data = await wishlistAPI.getWishlist();
      setWishlist(data);
    } catch (e) {
      Alert.alert('Error', 'Failed to load wishlist');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadWishlist();
    setRefreshing(false);
  };

  const handleRemove = async (itemId: string) => {
    try {
      await wishlistAPI.removeProduct(itemId);
      Alert.alert('Removed', 'Item removed from wishlist');
      await loadWishlist();
    } catch (e) {
      Alert.alert('Error', 'Failed to remove item');
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </SafeAreaView>
    );
  }

  const items = wishlist?.items || [];

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Wishlist</Text>
        <Text style={styles.count}>{items.length} items</Text>
      </View>

      {items.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No items in wishlist</Text>
          <Text style={styles.emptySubtext}>Search for products to add them</Text>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.itemCard}>
              <View style={styles.itemContent}>
                <Text style={styles.productName} numberOfLines={2}>
                  {item.products?.name || 'Unknown Product'}
                </Text>
                <View style={styles.priceRow}>
                  <Text style={styles.currentPrice}>
                    ₹{item.products?.current_price || 'N/A'}
                  </Text>
                  {item.price_when_added && (
                    <Text style={styles.addedPrice}>
                      Added: ₹{item.price_when_added}
                    </Text>
                  )}
                </View>
                <Text style={styles.platform}>
                  {item.products?.platform || 'Multiple platforms'}
                </Text>
              </View>
              
              <TouchableOpacity 
                style={styles.removeBtn}
                onPress={() => handleRemove(item.id)}
              >
                <Ionicons name="close-circle" size={24} color={COLORS.error} />
              </TouchableOpacity>
            </View>
          )}
          refreshing={refreshing}
          onRefresh={handleRefresh}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    padding: SPACING.lg,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderColor,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: 4,
  },
  count: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  itemCard: {
    flexDirection: 'row',
    padding: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderColor,
    alignItems: 'center',
  },
  itemContent: {
    flex: 1,
  },
  productName: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 4,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  currentPrice: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.primary,
  },
  addedPrice: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  platform: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  removeBtn: {
    padding: 8,
  },
});
```

---

### STEP 2: Fix Price History to Show Real Data

**File: SmartShopAI/app/track.tsx**

```tsx
// ❌ OLD: Generate dummy data
const generateGraphData = (basePrice: number) => {
  // ... generates same data for all products
};

// ✅ NEW: Fetch real data from API
const [graphData, setGraphData] = useState<any[]>([]);
const [priceLoading, setPriceLoading] = useState(true);

useEffect(() => {
  loadPriceHistory();
}, [productId]);

const loadPriceHistory = async () => {
  try {
    setPriceLoading(true);
    const response = await fetch(
      `http://localhost:8000/price-history/${productId}`
    );
    const data = await response.json();
    
    if (data.success && data.data_points) {
      setGraphData(data.data_points);
    } else {
      // Fallback to dummy if API fails
      setGraphData(generateDummyData());
    }
  } catch (e) {
    setGraphData(generateDummyData());
  } finally {
    setPriceLoading(false);
  }
};

// Only generate dummy if API fails
const generateDummyData = () => {
  // Generate based on productId so it's at least different per product
  const seed = parseInt(productId) || Math.random();
  // ... generate based on seed
};
```

---

### STEP 3: Fix Deal Alerts

**File: utils/scheduler.py (Create if doesn't exist)**

```python
"""
Background scheduler for price monitoring and alerts
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from utils.logger import app_logger
from utils.supabase_client import db as supabase_db
from utils.whatsapp_notifier import whatsapp_notifier
from utils.email_sender import send_email
import requests
from datetime import datetime

scheduler = BackgroundScheduler()

def check_price_alerts():
    """Check all active alerts and send notifications"""
    try:
        app_logger.info("🔍 Checking price alerts...")
        
        # Get all active alerts
        alerts = supabase_db.table('price_alerts')\
            .select('*, users(email, phone), products(name, current_price)')\
            .eq('is_active', True)\
            .execute()
        
        for alert in alerts.data or []:
            product = alert.get('products', {})
            user = alert.get('users', {})
            current_price = product.get('current_price')
            alert_threshold = alert.get('alert_threshold')
            
            # Check if price has dropped below threshold
            if current_price and alert_threshold and current_price <= alert_threshold:
                # Send email alert
                send_email(
                    to=user.get('email'),
                    subject=f"🎉 Price Drop! {product.get('name')}",
                    body=f"""
                    Price Alert: {product.get('name')}
                    
                    Current Price: ₹{current_price}
                    Your Target: ₹{alert_threshold}
                    
                    Buy now: [link to product]
                    """
                )
                
                # Send WhatsApp alert
                if user.get('phone'):
                    try:
                        whatsapp_notifier.send_price_drop_alert(
                            user_phone=user.get('phone'),
                            product_name=product.get('name'),
                            previous_price=alert.get('price_when_added'),
                            new_price=current_price,
                            platform=product.get('platform'),
                            product_url=product.get('platform_url')
                        )
                    except Exception as e:
                        app_logger.warning(f"WhatsApp alert failed: {e}")
                
                # Update alert as triggered
                supabase_db.table('price_alerts')\
                    .update({'last_triggered': datetime.now()})\
                    .eq('id', alert.get('id'))\
                    .execute()
                
                app_logger.info(f"✅ Alert sent for {product.get('name')}")
    
    except Exception as e:
        app_logger.error(f"Error checking alerts: {e}")

# Schedule to run every 6 hours
def start_scheduler():
    """Start background scheduler"""
    try:
        scheduler.add_job(
            check_price_alerts,
            trigger=IntervalTrigger(hours=6),
            id='price_alerts_check',
            name='Price Alerts Checker'
        )
        scheduler.start()
        app_logger.info("✅ Background scheduler started")
    except Exception as e:
        app_logger.error(f"Failed to start scheduler: {e}")

def stop_scheduler():
    """Stop background scheduler"""
    try:
        scheduler.shutdown()
        app_logger.info("✅ Background scheduler stopped")
    except Exception as e:
        app_logger.error(f"Failed to stop scheduler: {e}")
```

**Update main.py to start scheduler:**

```python
# File: main.py (at the end before uvicorn.run)

# Import scheduler
from utils.scheduler import start_scheduler, stop_scheduler

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on app startup"""
    app_logger.info("🚀 Application starting...")
    start_scheduler()  # ✅ Start background jobs

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on app shutdown"""
    app_logger.info("🛑 Application shutting down...")
    stop_scheduler()  # ✅ Stop background jobs

if __name__ == "__main__":
    uvicorn.run("main:app", ...)
```

---

### STEP 4: Test AI Predictions

**Create test endpoint:**

```python
# File: main.py

@app.get("/api/test/prediction/{product_id}")
async def test_prediction(product_id: int):
    """Test endpoint to verify AI prediction works"""
    try:
        # Get product
        product = supabase_db.table('products')\
            .select('*')\
            .eq('id', product_id)\
            .single()\
            .execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get price history
        history = supabase_db.table('price_history')\
            .select('price, recorded_at')\
            .eq('product_id', product_id)\
            .order('recorded_at', desc=True)\
            .limit(30)\
            .execute()
        
        # Run prediction through Agent 4
        from agents.ai_predictor import ai_predictor_agent
        
        result = await ai_predictor_agent({
            'product_name': product.data['name'],
            'current_price': product.data['current_price'],
            'price_history': history.data,
        })
        
        return {
            'success': True,
            'product': product.data,
            'prediction': result
        }
    
    except Exception as e:
        app_logger.error(f"Prediction test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Test via terminal:**
```bash
# Test AI prediction
curl -X GET "http://localhost:8000/api/test/prediction/1"
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Critical Fixes (This Week)
- [ ] Fix wishlist endpoint (backend)
- [ ] Update wishlist API calls (frontend)
- [ ] Create wishlist display tab
- [ ] Test end-to-end wishlist workflow
- [ ] Test deal alerts scheduler
- [ ] Verify WhatsApp alerts work

### Phase 2: Feature Enhancements (Next Week)
- [ ] Implement product comparison
- [ ] Fix price history charts (use real data)
- [ ] Test AI predictions thoroughly
- [ ] Add affiliate links to results
- [ ] Performance optimization

### Phase 3: Polish (Following Week)
- [ ] UI/UX improvements
- [ ] Error message improvements
- [ ] Add loading states
- [ ] Cache optimization

---

## 🧪 TESTING PROCEDURES

### Test Wishlist
```bash
# 1. Add to wishlist
curl -X POST http://localhost:8000/api/wishlist/add \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "1", "target_price": 50000}'

# 2. Get wishlist
curl -X GET http://localhost:8000/api/wishlist \
  -H "Authorization: Bearer TOKEN"

# 3. Remove item
curl -X DELETE http://localhost:8000/api/wishlist-items/ITEM_ID \
  -H "Authorization: Bearer TOKEN"
```

### Test Alerts
```bash
# Send test alert
curl -X POST http://localhost:8000/api/send-alert-test \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "product_name": "iPhone 14 Pro",
    "previous_price": 99999,
    "current_price": 79999
  }'
```

### Test AI Prediction
```bash
curl -X GET http://localhost:8000/api/test/prediction/1
```

---

## 🔗 KEY FILES TO MODIFY

```
Backend:
├── main.py (Fix endpoints)
├── utils/scheduler.py (NEW - Create)
├── utils/wishlist_service.py (Already exists, verify)
└── agents/ai_predictor.py (Verify working)

Frontend:
├── SmartShopAI/utils/api.ts (NEW - Create)
├── SmartShopAI/app/track.tsx (Update display)
├── SmartShopAI/app/(tabs)/track.tsx (NEW - Wishlist tab)
└── SmartShopAI/constants/api-config.ts (Update)
```

---

## 📞 DEBUGGING TIPS

**Issue: Wishlist items not showing**
1. Check browser console for API errors
2. Verify token is being sent
3. Check backend logs: `docker logs smartshop-api`
4. Verify user has default wishlist: `SELECT * FROM wishlists WHERE user_id = 'USER_ID'`
5. Check wishlist items table: `SELECT * FROM wishlist_items WHERE wishlist_id = 'WISHLIST_ID'`

**Issue: Alerts not sending**
1. Check Twilio credentials in .env
2. Verify phone number format (with country code)
3. Check email sending logs
4. Verify scheduler is running: Check logs for "Background scheduler started"

**Issue: AI predictions not working**
1. Test Cohere API key: `curl -X POST https://api.cohere.ai/v1/...`
2. Check agent logs for errors
3. Test endpoint: `GET /api/test/prediction/1`

---

**Document End**

*This guide should be implemented in order. Start with Phase 1 (Critical Fixes) before moving to Phase 2.*
