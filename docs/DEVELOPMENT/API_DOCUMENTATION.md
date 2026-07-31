# SmartShop AI API Documentation

## Overview
The SmartShop AI API provides price tracking, explainable deal signals, product recommendations, and alert management for a mobile shopping application. Built with FastAPI, it integrates with Supabase for data storage.

## Base URL
```
http://localhost:8000/api
```

## Authentication
Authentication is OTP-based.

1. Request OTP:
```
POST /auth/request-otp
{
  "email": "user@example.com"
}
```

2. Verify OTP:
```
POST /auth/verify-otp
{
  "email": "user@example.com",
  "otp": "123456"
}
```

3. Use returned `user_id` for protected endpoints with Bearer auth:
```
Authorization: Bearer <user_id>
```

JWT signup/login endpoints are intentionally removed in OTP-only mode.

---

## Price Tracker Endpoints

### Get Price History
Get historical price data for a product.

**Endpoint:** `GET /price-tracker/history`

**Query Parameters:**
- `product_id` (string, required): Product identifier
- `days` (integer, optional, default=30): Number of days of history (1-365)

**Response:**
```json
{
  "product_id": "prod_123",
  "current_price": 1299.99,
  "lowest_price": 999.99,
  "highest_price": 1499.99,
  "average_price": 1199.99,
  "price_trend": "down",
  "days_tracked": 30,
  "history": [
    {
      "date": "2024-01-15",
      "price": 1299.99,
      "platform": "Amazon"
    }
  ]
}
```

### Get Buy Recommendation
Get AI recommendation for when to buy a product.

**Endpoint:** `GET /price-tracker/recommendation`

**Query Parameters:**
- `product_id` (string, required): Product identifier

**Response:**
```json
{
  "product_id": "prod_123",
  "recommendation": "buy_now|wait_few_days|wait",
  "reason": "Current price is near lowest",
  "confidence": 0.95,
  "current_price": 1299.99,
  "wait_days": 0,
  "deal_signal": "GENUINE_BARGAIN|FAKE_DISCOUNT|NORMAL|INSUFFICIENT_DATA",
  "deal_score": 0.95,
  "deal_message": "Current price is a real 30-day low and well below average."
}
```

**Recommendation Types:**
- `buy_now` (0.75-0.95 confidence): Price is favorable
- `wait_few_days` (0.65-0.75 confidence): Price likely to drop soon
- `wait` (0.50-0.70 confidence): No immediate urgency

### Track Price Change
Track a price change and generate alerts if needed.

**Endpoint:** `POST /price-tracker/track`

**Query Parameters:**
- `product_id` (string, required): Product identifier
- `platform_id` (string, required): Platform identifier (e.g., "amazon", "flipkart")
- `new_price` (float, required): Current price

**Response:**
```json
{
  "success": true,
  "price_change": {
    "product_id": "prod_123",
    "platform_id": "amazon",
    "previous_price": 1399.99,
    "new_price": 1299.99,
    "change_amount": 100.0,
    "change_percent": 7.14,
    "is_drop": true
  },
  "alert_created": true
}
```

### Get Deal Signal
Get explainable deal classification using deterministic pricing rules.

**Endpoint:** `GET /price-tracker/deal-signal`

**Query Parameters:**
- `product_id` (string, required): Product identifier
- `days` (integer, optional, default=30): Lookback window (7-365)

**Response:**
```json
{
  "product_id": "prod_123",
  "days": 30,
  "deal_signal": "GENUINE_BARGAIN",
  "deal_score": 0.95,
  "current_price": 1299.99,
  "average_price": 1499.99,
  "lowest_price": 1299.99,
  "recommendation": "buy_now",
  "reason": "Detected genuine bargain based on 30-day history"
}
```

---

## Recommendation Endpoints

### Get Personalized Recommendations
Get AI-powered product recommendations for a user.

**Endpoint:** `GET /recommendations/personalized`

**Query Parameters:**
- `user_id` (string, required): User identifier

**Response:**
```json
{
  "user_id": "user_123",
  "timestamp": "2024-01-20T10:30:00Z",
  "recommendations": [
    {
      "product_id": "prod_123",
      "product_name": "Wireless Headphones",
      "reason": "Wishlist item on sale: Price drop of 15%",
      "score": 0.95,
      "current_price": 1999.99,
      "discount_available": true,
      "buy_url": "https://www.amazon.in/dp/B0XXXXXXX"
    }
  ],
  "bundle_suggestions": [
    {
      "main_product": "prod_123",
      "bundle_with": ["prod_124", "prod_125"],
      "savings_percentage": 10
    }
  ]
}
```

### Get Browsing History
Retrieve user's product browsing history.

**Endpoint:** `GET /recommendations/browsing-history`

**Query Parameters:**
- `user_id` (string, required): User identifier
- `limit` (integer, optional, default=20, max=100): Number of items

**Response:**
```json
{
  "items": [
    {
      "id": "prod_123",
      "name": "Product Name",
      "category": "Electronics",
      "avg_rating": 4.5
    }
  ]
}
```

### Get Wishlist
Retrieve user's wishlist items.

**Endpoint:** `GET /recommendations/wishlist`

**Query Parameters:**
- `user_id` (string, required): User identifier

**Response:**
```json
{
  "items": [
    {
      "id": "prod_123",
      "name": "Product Name",
      "category": "Electronics",
      "avg_rating": 4.5,
      "min_price": 999.99
    }
  ]
}
```

### Get Category Trends
Get trending products in a category.

**Endpoint:** `GET /recommendations/category-trends`

**Query Parameters:**
- `category` (string, required): Product category
- `limit` (integer, optional, default=10, max=50): Number of items

**Response:**
```json
{
  "trends": [
    {
      "id": "prod_123",
      "name": "Trending Product",
      "avg_rating": 4.7,
      "view_count": 5000,
      "min_price": 1299.99
    }
  ]
}
```

---

## Alert Endpoints

### Get User Alerts
Retrieve alerts for a user.

**Endpoint:** `GET /alerts/user`

**Query Parameters:**
- `user_id` (string, required): User identifier
- `unread_only` (boolean, optional, default=false): Only unread alerts

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_123",
      "user_id": "user_123",
      "alert_type": "price_drop",
      "title": "Price Drop Alert",
      "message": "Product X is now 15% cheaper!",
      "product_id": "prod_123",
      "read": false,
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

**Alert Types:**
- `price_drop`: Price reduced by threshold
- `price_milestone`: Price reached target
- `back_in_stock`: Product available again
- `deal_expiring`: Limited offer ending soon

---

## Model Notes

- Direct-link mode is the default project model.
- Affiliate links are optional and not required for API functionality.
- Deal signal classification is explainable and rule-based (no hidden scoring).

### Mark Alert as Read
Mark an alert as read.

**Endpoint:** `POST /alerts/{alert_id}/read`

**Path Parameters:**
- `alert_id` (string, required): Alert identifier

**Response:**
```json
{
  "success": true
}
```

### Delete Alert
Delete an alert.

**Endpoint:** `DELETE /alerts/{alert_id}`

**Path Parameters:**
- `alert_id` (string, required): Alert identifier

**Response:**
```json
{
  "success": true
}
```

---

## Error Handling

All errors return a standard format:

```json
{
  "detail": "Error description"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad request (missing/invalid parameters)
- `401`: Unauthorized
- `404`: Resource not found
- `500`: Server error

---

## Rate Limiting

- Default: 100 requests per minute per IP
- Authenticated users: 500 requests per minute

---

## Examples

### Python (requests)
```python
import requests

api_base = "http://localhost:8000/api"

# Get price history
response = requests.get(
    f"{api_base}/price-tracker/history",
    params={"product_id": "prod_123", "days": 30}
)
price_data = response.json()

# Get recommendations
response = requests.get(
    f"{api_base}/recommendations/personalized",
    params={"user_id": "user_123"}
)
recommendations = response.json()
```

### JavaScript (fetch)
```javascript
const apiBase = "http://localhost:8000/api";

// Get price history
const response = await fetch(
  `${apiBase}/price-tracker/history?product_id=prod_123&days=30`
);
const priceData = await response.json();

// Track price change
const trackResponse = await fetch(
  `${apiBase}/price-tracker/track?` +
  `product_id=prod_123&platform_id=amazon&new_price=1299.99`,
  { method: 'POST' }
);
```

---

## Webhook Events

Subscribe to real-time events via webhook:

```json
{
  "event": "price_drop|recommendation_generated|alert_triggered",
  "data": { /* event-specific data */ },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

Configure webhooks in the admin panel or via API.

---

## Support

For API questions and issues:
- Email: support@smartshop.ai
- Documentation: https://docs.smartshop.ai
- Status: https://status.smartshop.ai
