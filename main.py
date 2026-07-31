from fastapi import FastAPI, HTTPException, status, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
import json
import os
import uvicorn
from datetime import datetime, timedelta
import traceback

load_dotenv()

from graph.pipeline import run_price_pipeline
from utils.validators import validate_email, validate_product_name, validate_otp, validate_user_id
from utils.logger import app_logger
from utils.cache import cache, cached, cache_invalidate

from utils.price_charts import PriceChartManager
from utils.supabase_client import db as supabase_db

# Product & Wishlist services
from utils.product_service import (
    ProductCreate, Product, ProductComparison, SearchResponse,
    generate_product_hash, generate_canonical_name, search_products,
    get_product_with_prices,
)
from utils.wishlist_service import (
    WishlistResponse, WishlistItemResponse, PriceAlertResponse,
    get_user_wishlists, get_wishlist_with_items, add_to_wishlist,
    remove_from_wishlist, mark_item_purchased, get_price_alerts,
)
from utils.whatsapp_notifier import whatsapp_notifier

# Agents (merged from api.py)
from agents.product_scraper import ProductScraper
from agents.price_tracker import PriceTracker
from agents.recommendation_engine import RecommendationEngine
from agents.deal_signal import evaluate_from_history
import asyncio

app = FastAPI(
    title="AI Price Intelligence API",
    description="5-agent AI system for price tracking and predictions",
    version="1.1.0"
)

# CORS with proper configuration from environment
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8081,http://127.0.0.1:8081",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ==================== DEPENDENCY FOR AUTHENTICATION ====================
async def get_current_user(authorization: str = Header(None)) -> str:
    """Extract user ID from Authorization header (Bearer <user_id>)."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split(maxsplit=1)
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")

        user_id = token.strip()
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user_id token")

        return user_id
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format")
    except HTTPException:
        raise

class SearchRequest(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=200)
    user_email: str

class StatusUpdate(BaseModel):
    product_id: int = Field(..., gt=0)
    status: str = Field(..., pattern="^(Tracking|Purchased|Cancelled)$")

class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str = Field(..., pattern="^\\d{6}$")

class TrackRequest(BaseModel):
    user_id: str = Field(..., min_length=5)
    product_name: str = Field(..., min_length=2, max_length=200)
    price: str
    url: str
    platform: str = "Amazon"

class AddToWishlistRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    product_name: Optional[str] = None  # For creating products on-demand
    platform: Optional[str] = None      # For creating products on-demand
    target_price: Optional[float] = None
    initial_price: Optional[float] = None

@app.get("/api/health")
def health_check():
    """API health check"""
    db_status = supabase_db.health_check()
    return {
        "status": "healthy",
        "message": "AI Price Intelligence API v2.0.0",
        "version": "2.0.0",
        "database": db_status["status"],
        "timestamp": datetime.now().isoformat(),
    }


@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {}

@app.post("/api/analyze")
@app.post("/api/search")
async def analyze_product(request: SearchRequest):
    """Analyze product using 5-agent pipeline - returns TOP 5 best products"""
    try:
        is_valid_product, product_error = validate_product_name(request.product_name)
        if not is_valid_product:
            raise HTTPException(status_code=422, detail=product_error)
        
        is_valid_email, email_error = validate_email(request.user_email)
        if not is_valid_email:
            raise HTTPException(status_code=422, detail=email_error)
        
        app_logger.info(f"Analyzing: {request.product_name}")
        result = run_price_pipeline(request.product_name, request.user_email)
        
        # Extract best 5 products with clean formatting
        best_5 = result.get("best_5_products", result.get("products_found", []))[:5]
        
        return {
            "success": True,
            "product_name": request.product_name,
            "total_found": result.get("total_found", len(best_5)),
            "best_5_products": best_5,  # TOP 5 sorted by comprehensive scoring
            "products_found": best_5,    # Same as best_5 for compatibility
            "ai_prediction": result.get("ai_prediction", ""),
            "alert_status": result.get("alert_status", ""),
            "best_product": best_5[0] if best_5 else {}  # Best overall product
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze product")
@app.post("/api/auth/request-otp")
@app.post("/api/auth/otp/request")
async def request_otp_endpoint(req: OTPRequest):
    """Request OTP for authentication"""
    try:
        from utils.auth import request_otp as _request_otp
        is_valid, error_msg = validate_email(req.email)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)
        app_logger.info(f"OTP requested for: {req.email}")
        result = _request_otp(req.email)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send OTP"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"OTP request error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@app.post("/api/auth/verify-otp")
@app.post("/api/auth/otp/verify")
async def verify_otp_endpoint(req: OTPVerify):
    """Verify OTP"""
    try:
        from utils.auth import verify_otp as _verify_otp
        is_valid, error_msg = validate_otp(req.otp)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)
        app_logger.info(f"OTP verification for: {req.email}")
        result = _verify_otp(req.email, req.otp)
        if not result.get("success"):
            error_message = str(result.get("error", "OTP verification failed"))
            lowered = error_message.lower()
            if "not found" in lowered:
                status_code = 404
            elif "invalid otp" in lowered or "expired" in lowered:
                status_code = 401
            else:
                status_code = 400
            raise HTTPException(status_code=status_code, detail=error_message)
        return result
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"OTP verify error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify OTP")


# REMOVED: Legacy JSON track/tracked endpoints. 
# Use /api/wishlists for database-backed tracking.


# ── WISHLIST ENDPOINTS ────────────────────────
@app.get("/api/wishlist/{user_id}")
async def get_user_wishlist_items(user_id: str):

    """Get user's wishlist items from DB"""
    try:
        is_valid, error_msg = validate_user_id(user_id)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)

        app_logger.info(f"Retrieving wishlist for {user_id}")

        # Get user's wishlists from the real DB
        wishlists = get_user_wishlists(user_id)
        all_items = []
        for wl in wishlists:
            try:
                full_wl = get_wishlist_with_items(wl.id, user_id)
                for item in full_wl.items:
                    all_items.append({
                        "id": item.id,
                        "name": item.product_name,
                        "brand": item.product_brand,
                        "price": item.current_best_price or item.price_when_added,
                        "price_when_added": item.price_when_added,
                        "target_price": item.target_price,
                        "platform": item.current_best_platform or "Unknown",
                        "image_url": item.product_image_url,
                        "is_purchased": item.is_purchased,
                        "savings": round(item.price_when_added - (item.current_best_price or item.price_when_added), 2),
                    })
            except Exception:
                continue

        return {"success": True, "wishlist": all_items, "total": len(all_items)}
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Wishlist get error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch wishlist")

# ── DASHBOARD ENDPOINTS ────────────────────────
@app.get("/api/dashboard/{user_id}")
@cached(ttl=120, key_prefix="dashboard")
async def get_dashboard(user_id: str):

    """Get user dashboard with REAL stats from database"""
    try:
        is_valid, error_msg = validate_user_id(user_id)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)

        app_logger.info(f"Dashboard accessed by {user_id}")

        # ── Real stats from DB ──
        total_tracked = 0
        total_saved = 0.0
        price_drops = 0
        alerts_count = 0
        recent_activity = []

        try:
            wishlists = get_user_wishlists(user_id)
            for wl in wishlists:
                try:
                    full_wl = get_wishlist_with_items(wl.id, user_id)
                    total_tracked += len(full_wl.items)
                    for item in full_wl.items:
                        if item.current_best_price and item.price_when_added:
                            savings = item.price_when_added - item.current_best_price
                            if savings > 0:
                                total_saved += savings
                                price_drops += 1
                except Exception:
                    continue
        except Exception:
            pass

        try:
            user_alerts = get_price_alerts(user_id, limit=50)
            alerts_count = len(user_alerts)
            for alert in user_alerts[:10]:
                recent_activity.append({
                    "action": "price_drop",
                    "product": alert.product_name,
                    "drop": round(alert.price_drop_amount, 2),
                    "platform": alert.platform_name,
                    "timestamp": alert.created_at.isoformat() if alert.created_at else None,
                })
        except Exception:
            pass

        return {
            "success": True,
            "stats": {
                "total_tracked": total_tracked,
                "total_saved": round(total_saved, 2),
                "price_drops": price_drops,
                "alerts": alerts_count,
            },
            "recent_activity": recent_activity,
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard")

# ── DEALS & COMPARISON ENDPOINTS ────────────────────────
@app.get("/api/deals")
@cached(ttl=300, key_prefix="deals")
async def get_trending_deals():

    """Get real deals: products with biggest recent price drops from DB"""
    try:
        app_logger.info("Trending deals requested")

        # Query products with significant price drops in the last 7 days
        date_threshold = (datetime.now() - timedelta(days=7)).isoformat()
        deals = []

        try:
            # Get all products that have recent prices
            products_result = supabase_db.table('products').select(
                'id, name, brand, image_url, average_rating'
            ).limit(50).execute()

            for product in (products_result.data or []):
                pid = product['id']
                # Get latest and previous prices
                prices_result = supabase_db.table('product_prices').select(
                    'price, original_price, discount_percent, product_url, last_checked, platforms(name)'
                ).eq('product_id', pid).order(
                    'last_checked', desc=True
                ).limit(5).execute()

                if not prices_result.data or len(prices_result.data) < 1:
                    continue

                latest = prices_result.data[0]
                current_price = latest['price']
                original_price = latest.get('original_price') or current_price
                discount = latest.get('discount_percent') or 0

                # Calculate discount from history if not explicit
                if discount == 0 and len(prices_result.data) >= 2:
                    prev_price = prices_result.data[-1]['price']
                    if prev_price > current_price:
                        discount = round((prev_price - current_price) / prev_price * 100, 1)
                        original_price = prev_price

                if discount >= 5:  # Only show deals with 5%+ discount
                    # Get deal signal
                    price_list = [p['price'] for p in reversed(prices_result.data)]
                    deal_info = evaluate_from_history(price_list)

                    deals.append({
                        "id": pid,
                        "name": product['name'],
                        "brand": product.get('brand', ''),
                        "image_url": product.get('image_url'),
                        "original_price": original_price,
                        "current_price": current_price,
                        "discount_percent": round(discount, 1),
                        "platform": latest.get('platforms', {}).get('name', 'Unknown'),
                        "rating": product.get('average_rating'),
                        "product_url": latest.get('product_url', ''),
                        "deal_signal": deal_info.get('label', 'NORMAL'),
                        "deal_score": deal_info.get('score', 0.5),
                        "deal_message": deal_info.get('message', ''),
                    })

            # Sort by discount percent descending
            deals.sort(key=lambda d: d['discount_percent'], reverse=True)
        except Exception as e:
            app_logger.warning(f"Deals DB query failed, returning empty: {e}")

        return {"success": True, "deals": deals[:20], "total": len(deals)}
    except Exception as e:
        app_logger.error(f"Deals error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch deals")

@app.post("/api/compare")
@cached(ttl=600, key_prefix="compare")
async def compare_prices(req: SearchRequest):

    """Compare product prices across platforms using DB data"""
    try:
        is_valid_product, product_error = validate_product_name(req.product_name)
        if not is_valid_product:
            raise HTTPException(status_code=422, detail=product_error)

        app_logger.info(f"Price comparison for: {req.product_name}")

        comparison = []
        try:
            # Search products in DB
            search_result = search_products(req.product_name, limit=10)
            for product in search_result.products:
                for price_opt in product.price_options:
                    comparison.append({
                        "platform": price_opt.platform_name,
                        "price": price_opt.price,
                        "original_price": price_opt.original_price,
                        "rating": price_opt.rating,
                        "in_stock": price_opt.in_stock,
                        "url": price_opt.product_url,
                        "product_name": product.product_name,
                    })

            # Sort by price
            comparison.sort(key=lambda c: c['price'])
        except Exception as e:
            app_logger.warning(f"DB comparison failed: {e}")

        return {
            "success": True,
            "product": req.product_name,
            "comparison": comparison,
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Price comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compare prices")


# ── PRICE CHARTS & HISTORY ENDPOINTS ────────────────────────
@app.get("/price-history/{product_id}")
@cached(ttl=600, key_prefix="price_history")  # Cache for 10 minutes
async def get_price_history(product_id: int, days: int = 30):
    """Get price history and trend for a product
    
    Returns:
    - min_price: Lowest price in period
    - max_price: Highest price in period
    - avg_price: Average price
    - trend: 'up' | 'down' | 'stable'
    - change_percent: Price change percentage
    - data_points: Array of {date, price, platform}
    """
    try:
        if product_id <= 0:
            raise HTTPException(status_code=422, detail="Invalid product ID")
        
        trend_data = PriceChartManager.get_price_trend(product_id, days)
        
        if trend_data.get("status") == "error":
            raise HTTPException(status_code=500, detail=trend_data.get("message"))
        
        app_logger.info(f"Price history retrieved for product {product_id}")
        return {"success": True, **trend_data}
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Price history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch price history")


@app.get("/price-prediction/{product_id}")
@cached(ttl=3600, key_prefix="price_prediction")  # Cache for 1 hour
async def get_price_prediction(product_id: int):
    """Get predicted price and buying recommendation
    
    Returns:
    - predicted_price: Estimated price for next 7 days
    - trend: Current trend direction
    - confidence: 'high' or 'low'
    - recommendation: Buying recommendation message
    """
    try:
        if product_id <= 0:
            raise HTTPException(status_code=422, detail="Invalid product ID")
        
        prediction = PriceChartManager.get_price_prediction(product_id)
        
        if prediction.get("status") == "error":
            raise HTTPException(status_code=500, detail=prediction.get("message"))
        
        app_logger.info(f"Price prediction retrieved for product {product_id}")
        return {"success": True, **prediction}
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Price prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate prediction")


@app.get("/best-price-day/{product_id}")
@cached(ttl=3600, key_prefix="best_price_day")  # Cache for 1 hour
async def get_best_price_day(product_id: int, days: int = 30):
    """Get the day with lowest price in date range
    
    Returns:
    - date: Date with lowest price
    - price: Lowest price value
    - platform: Platform with lowest price
    - savings: Potential savings vs highest price
    """
    try:
        if product_id <= 0:
            raise HTTPException(status_code=422, detail="Invalid product ID")
        
        best_day = PriceChartManager.get_best_price_day(product_id, days)
        
        if not best_day:
            raise HTTPException(status_code=404, detail="No price history available")
        
        app_logger.info(f"Best price day retrieved for product {product_id}")
        return {"success": True, "best_price_day": best_day}
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Best price day error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get best price day")


@app.get("/savings-summary/{user_id}")
@cached(ttl=600, key_prefix="savings_summary")  # Cache for 10 minutes
async def get_savings_summary(user_id: str):
    """Get total potential savings across all tracked products
    
    Returns:
    - total_potential_savings: Total savings opportunity
    - products_tracked: Total tracked products
    - products_with_history: Products with price history
    - avg_savings_per_product: Average savings per product
    """
    try:
        is_valid, error_msg = validate_user_id(user_id)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)
        
        summary = PriceChartManager.get_savings_summary(user_id)
        
        if summary.get("status") == "error":
            raise HTTPException(status_code=500, detail=summary.get("message"))
        
        app_logger.info(f"Savings summary retrieved for user {user_id}")
        return {"success": True, **summary}
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Savings summary error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch savings summary")


@app.get("/cache-status")
async def get_cache_status():
    """Get cache system status and statistics"""
    try:
        cache_type = "Redis" if cache.use_redis else "Memory"
        cache_size = len(cache.memory_cache) if not cache.use_redis else "unknown"
        
        return {
            "success": True,
            "cache_type": cache_type,
            "cache_size": cache_size,
            "status": "healthy"
        }
    except Exception as e:
        app_logger.error(f"Cache status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cache status")


@app.delete("/cache/clear")
@cache_invalidate("*")  # Invalidate all caches when this endpoint is called
async def clear_cache():
    """Clear all cached data"""
    try:
        cache.clear()
        app_logger.info("✅ All cache cleared")
        return {"success": True, "message": "Cache cleared successfully"}       
    except Exception as e:
        app_logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")    


# ==================== NEW MULTI-PLATFORM API ENDPOINTS ====================

# ============ PRODUCT SEARCH ENDPOINTS ============

@app.get("/api/products/search", response_model=SearchResponse)
async def search_products_api(q: str, category: str = None, limit: int = 20):
    """
    Search for products across all platforms
    
    Query Parameters:
    - q: Search query (e.g., "moto g65 smartphone")
    - category: Optional category filter
    - limit: Max results (default 20)
    """
    if len(q) < 2:
        raise HTTPException(status_code=422, detail="Search query must be at least 2 characters")
    
    return search_products(q.strip(), category, limit)

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get product details with all prices across platforms"""
    return get_product_with_prices(product_id)

# ============ WISHLIST ENDPOINTS ============

@app.get("/api/wishlists", response_model=list)
async def list_wishlists(current_user: str = Depends(get_current_user)):
    """Get all wishlists for current user"""
    return get_user_wishlists(current_user)

@app.get("/api/wishlists/{wishlist_id}", response_model=WishlistResponse)
async def get_wishlist(wishlist_id: str, current_user: str = Depends(get_current_user)):
    """Get wishlist with all items"""
    return get_wishlist_with_items(wishlist_id, current_user)

@app.post("/api/wishlist/add")
async def add_product_to_wishlist(
    request: AddToWishlistRequest,
    current_user: str = Depends(get_current_user)
):
    """Add product to user's default wishlist"""
    try:
        import uuid as uuid_module
        
        app_logger.info(f"📌 Adding product {request.product_id} to wishlist for user {current_user}")
        
        # Check if product_id is a valid UUID
        try:
            uuid_module.UUID(request.product_id)
            product_id = request.product_id
        except ValueError:
            # Not a UUID - create product if name is provided
            if request.product_name:
                app_logger.info(f"🆕 Creating product: {request.product_name}")
                product_insert = {
                    'name': request.product_name,
                    'brand': 'Unknown',
                    'is_active': True
                }
                product_result = supabase_db.table('products').insert(product_insert).execute()
                if product_result.data:
                    product_id = product_result.data[0]['id']
                    app_logger.info(f"✅ Product created: {product_id}")
                else:
                    raise HTTPException(status_code=500, detail="Failed to create product")
            else:
                raise HTTPException(status_code=400, detail="Invalid product_id and no product_name provided")
        
        # Get user's default wishlist
        wishlist_result = supabase_db.table('wishlists')\
            .select('id')\
            .eq('user_id', current_user)\
            .eq('is_default', True)\
            .execute()
        
        if not wishlist_result.data:
            # Create default wishlist if doesn't exist
            app_logger.warning(f"⚠️ Default wishlist not found for {current_user}, creating...")
            create_result = supabase_db.table('wishlists').insert({
                'user_id': current_user,
                'name': 'My Wishlist',
                'is_default': True,
                'is_public': False
            }).execute()
            
            if not create_result.data:
                raise HTTPException(status_code=500, detail="Failed to create wishlist")
            
            wishlist_id = create_result.data[0]['id']
        else:
            wishlist_id = wishlist_result.data[0]['id']
        
        # Add to wishlist using the service
        from utils.wishlist_service import add_to_wishlist as _add_to_wishlist
        result = _add_to_wishlist(
            wishlist_id, 
            current_user, 
            product_id,  # Use the UUID (either provided or created)
            request.target_price
        )

        # Ensure product has a price record in product_prices table
        try:
            existing_prices = supabase_db.table('product_prices')\
                .select('id')\
                .eq('product_id', product_id)\
                .limit(1)\
                .execute()
                
            if not existing_prices.data:
                price_to_store = request.initial_price or (request.target_price * 1.1 if request.target_price else 999.0)
                platform_name = request.platform or 'Amazon'
                plat_res = supabase_db.table('platforms').select('id').ilike('name', f"%{platform_name}%").limit(1).execute()
                plat_id = plat_res.data[0]['id'] if (plat_res.data and len(plat_res.data) > 0) else None
                
                price_insert = {
                    'product_id': product_id,
                    'price': price_to_store,
                    'original_price': price_to_store,
                    'in_stock': True,
                    'scrape_source': platform_name
                }
                if plat_id:
                    price_insert['platform_id'] = plat_id
                    
                supabase_db.table('product_prices').insert(price_insert).execute()
                app_logger.info(f"✅ Initial price {price_to_store} stored for product {product_id}")
        except Exception as price_err:
            app_logger.warning(f"Could not store initial price row: {price_err}")
        
        app_logger.info(f"✅ Product {product_id} added to wishlist")
        return {
            "success": True,
            "message": "Added to wishlist",
            "item": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error adding to wishlist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add to wishlist: {str(e)}")

@app.get("/api/wishlist")
async def get_user_default_wishlist(current_user: str = Depends(get_current_user)):
    """Get user's default wishlist with all items"""
    try:
        app_logger.info(f"📋 Fetching wishlist for user {current_user}")
        
        # Get user's default wishlist
        wishlist_result = supabase_db.table('wishlists')\
            .select('id')\
            .eq('user_id', current_user)\
            .eq('is_default', True)\
            .execute()
        
        if not wishlist_result.data:
            app_logger.warning(f"⚠️ Wishlist not found for {current_user}, returning empty")
            return {
                "wishlist_id": None,
                "items": []
            }
        
        wishlist_id = wishlist_result.data[0]['id']
        
        # Fetch items with product details
        items_result = supabase_db.table('wishlist_items')\
            .select('''
                id, 
                product_id, 
                price_when_added,
                target_price, 
                lowest_price_seen,
                added_at,
                products(id, name, image_url, brand)
            ''')\
            .eq('wishlist_id', wishlist_id)\
            .order('added_at', desc=True)\
            .execute()
        
        # For each item, get the current best price from product_prices
        enriched_items = []
        for item in (items_result.data or []):
            if not item or not isinstance(item, dict):
                app_logger.debug(f"Skipping invalid wishlist item row: {item}")
                continue
            product = item.get('products') or {}

            # Get the best current price for this product across all platforms
            prices_result = supabase_db.table('product_prices')\
                .select('price, product_url, platform_id, platforms(id, name, url, logo_url)')\
                .eq('product_id', item['product_id'])\
                .order('price', desc=False)\
                .limit(1)\
                .execute()

            current_price = 0
            platform_info = {}
            product_url = None

            try:
                if prices_result and getattr(prices_result, 'data', None):
                    row = prices_result.data[0] or {}
                    if isinstance(row, dict):
                        current_price = row.get('price', 0)
                        product_url = row.get('product_url')
                        platform_info = row.get('platforms') or {}
                    else:
                        app_logger.warning(f"Unexpected price row shape for product {item.get('product_id')}: {type(row)}")
                else:
                    app_logger.debug(f"No price rows for product {item.get('product_id')}")
            except Exception as ex:
                app_logger.warning(f"Could not parse prices_result for product {item.get('product_id')}: {ex}")
                current_price = 0
                product_url = None
                platform_info = {}

            # Enrich the item with price info and keep product details
            item['price'] = current_price  # Current best price
            item['url'] = product_url or (product.get('url') if isinstance(product, dict) else None)

            # Platform name and logo fallback
            platform_name = 'Unknown'
            platform_logo = None
            if isinstance(platform_info, dict):
                try:
                    platform_name = platform_info.get('name') or 'Unknown'
                    platform_logo = platform_info.get('logo_url')
                except Exception:
                    platform_name = 'Unknown'
                    platform_logo = None

            item['platform'] = platform_name
            item['product_name'] = (product.get('name', 'Unknown') if isinstance(product, dict) else 'Unknown')
            item['product_image'] = (product.get('image_url') if isinstance(product, dict) else None)
            item['product_brand'] = (product.get('brand', 'Unknown') if isinstance(product, dict) else 'Unknown')

            # If product image is missing, fallback to platform logo if available
            item['image_url'] = (product.get('image_url') if isinstance(product, dict) and product.get('image_url') else platform_logo)

            enriched_items.append(item)
        
        app_logger.info(f"✅ Found {len(enriched_items)} items in wishlist")
        
        return {
            "wishlist_id": wishlist_id,
            "items": enriched_items
        }
    
    except Exception as e:
        tb = traceback.format_exc()
        app_logger.error(f"Error fetching wishlist: {e}\n{tb}")
        # Temporary verbose error for local debugging
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist: {str(e)}\n{tb}")

@app.delete("/api/wishlist-items/{item_id}")
async def remove_wishlist_item(item_id: str, current_user: str = Depends(get_current_user)):
    """Remove product from wishlist"""
    return remove_from_wishlist(item_id, current_user)

@app.post("/api/wishlist-items/{item_id}/purchased")
async def mark_purchased(
    item_id: str,
    platform_id: str,
    purchase_price: float,
    current_user: str = Depends(get_current_user)
):
    """Mark wishlist item as purchased"""
    return mark_item_purchased(item_id, current_user, platform_id, purchase_price)

# ============ PRICE ALERTS ENDPOINTS ============

@app.get("/api/price-alerts", response_model=list)
async def list_price_alerts(current_user: str = Depends(get_current_user)):
    """Get price alerts for user's products"""
    return get_price_alerts(current_user)

@app.post("/api/send-alert-test")
async def test_whatsapp_alert(
    phone: str,
    product_name: str = "iPhone 15",
    previous_price: float = 75000,
    current_user: str = Depends(get_current_user)
):
    """Test WhatsApp alert (admin only)"""
    try:
        success = whatsapp_notifier.send_price_drop_alert(
            phone,
            product_name,
            previous_price,
            previous_price - 5000,
            "Amazon India",
            "https://www.amazon.in/example"
        )
        return {
            "success": success,
            "message": "WhatsApp alert sent" if success else "Failed to send alert"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dev/insert-test-price")
async def dev_insert_test_price(
    product_id: str = None,
    price: float = 149900.0,
    platform_name: str = "Amazon India",
    product_image: str = None,
    current_user: str = Depends(get_current_user),
):
    """DEV only: insert a test product_prices row for UI testing."""
    try:
        # Default product id from existing wishlist if not provided
        default_product = product_id or 'b90a5702-edc9-4cfd-9ce3-1698e941f863'

        # Find platform id
        plat_res = supabase_db.table('platforms').select('id,name').eq('name', platform_name).limit(1).execute()
        if not plat_res.data:
            raise HTTPException(status_code=404, detail=f"Platform {platform_name} not found")
        platform_id = plat_res.data[0]['id']

        row = {
            'product_id': default_product,
            'platform_id': platform_id,
            'price': price,
            'original_price': price,
            'discount_percent': 0,
            'in_stock': True,
            'product_url': f'https://www.example.com/test/{default_product}',
            'rating': 4.5,
            'reviews_count': 1,
            'scrape_source': 'dev_insert'
        }

        # Optionally update product image on the product record so UI shows real image
        if product_image:
            try:
                supabase_db.table('products').update({'image_url': product_image}).eq('id', default_product).execute()
            except Exception as e:
                app_logger.warning(f"Failed to update product image for {default_product}: {e}")

        res = supabase_db.table('product_prices').insert(row).execute()
        return { 'success': True, 'inserted': res.data }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Dev insert failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ USER DASHBOARD ENDPOINTS ============

@app.get("/api/dashboard")
async def get_user_dashboard(current_user: str = Depends(get_current_user)):
    """Get personalized user dashboard"""
    try:
        # Resolve basic user profile from DB for OTP-only auth mode.
        user_result = (
            supabase_db
            .table("users")
            .select("id,email,first_name,last_name,notification_enabled")
            .eq("id", current_user)
            .limit(1)
            .execute()
        )
        user = user_result.data[0] if user_result.data else {
            "id": current_user,
            "email": None,
            "first_name": None,
            "last_name": None,
            "notification_enabled": True,
        }
        
        # Get wishlists
        wishlists = get_user_wishlists(current_user)
        
        # Get price alerts
        alerts = get_price_alerts(current_user, limit=10)
        
        # Calculate statistics
        total_wishlist_items = sum(w.item_count for w in wishlists)
        
        return {
            "success": True,
            "user": user,
            "wishlists": wishlists,
            "recent_alerts": alerts,
            "stats": {
                "total_wishlist_items": total_wishlist_items,
                "total_price_alerts": len(alerts),
                "notification_enabled": user.get("notification_enabled", True)
            }
        }
    except Exception as e:
        app_logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard")

# ============ PRODUCT SCRAPER ENDPOINTS ====================

@app.post("/api/scraper/search")
async def scraper_search_products(q: str, max_results: int = 10, user_id: str = Depends(get_current_user)):
    """Search and scrape products from all platforms"""
    try:
        async with ProductScraper() as scraper:
            all_products = await scraper.search_all_platforms(q, max_results)
            return {
                "query": q,
                "total_products": sum(len(p) for p in all_products.values()),
                "by_platform": {k: len(v) for k, v in all_products.items()},
                "products": all_products
            }
    except Exception as e:
        app_logger.error(f"Scraper search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.post("/api/scraper/populate")
async def scraper_populate_database(query: str = "iphone", user_id: str = Depends(get_current_user)):
    """Scrape products and populate database"""
    try:
        app_logger.info(f"Starting scraper for query: {query}")
        
        async with ProductScraper() as scraper:
            all_products = await scraper.search_all_platforms(query, max_results=5)
            saved_count = await scraper.save_products_to_db(all_products)
            
            return {
                "success": True,
                "query": query,
                "products_saved": saved_count,
                "message": f"Successfully scraped and saved {saved_count} products"
            }
    except Exception as e:
        app_logger.error(f"Scraper populate error: {e}")
        raise HTTPException(status_code=500, detail="Population failed")

@app.get("/api/scraper/status")
async def scraper_status(user_id: str = Depends(get_current_user)):
    """Get database product statistics"""
    try:
        products_result = supabase_db.table('products').select('id', count='exact').execute()
        prices_result = supabase_db.table('product_prices').select('id', count='exact').execute()
        
        return {
            "success": True,
            "total_products": products_result.count or 0,
            "total_prices": prices_result.count or 0,
            "message": "Database status retrieved"
        }
    except Exception as e:
        app_logger.error(f"Scraper status error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

# ============ MERGED FROM api.py — PRICE TRACKER ENDPOINTS ====================

@app.get("/api/price-tracker/history")
async def get_price_tracker_history(
    product_id: str,
    days: int = Query(30, ge=1, le=365),
):
    """Get price history for a product (from price_tracker agent)"""
    try:
        analysis = PriceTracker.get_price_history(product_id, days)
        return analysis.dict()
    except Exception as e:
        app_logger.error(f"Price tracker history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price-tracker/recommendation")
async def get_buy_recommendation(product_id: str):
    """Get AI buy/wait recommendation"""
    try:
        return PriceTracker.should_buy_now(product_id)
    except Exception as e:
        app_logger.error(f"Buy recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price-tracker/deal-signal")
async def get_deal_signal(
    product_id: str,
    days: int = Query(30, ge=7, le=365),
):
    """Explainable deal quality signal — GENUINE_BARGAIN / FAKE_DISCOUNT / NORMAL"""
    try:
        analysis = PriceTracker.get_price_history(product_id, days)
        recommendation = PriceTracker.should_buy_now(product_id)
        return {
            "product_id": product_id,
            "days": days,
            "deal_signal": analysis.deal_signal,
            "deal_score": analysis.deal_score,
            "current_price": analysis.current_price,
            "average_price": analysis.average_price,
            "lowest_price": analysis.lowest_price,
            "recommendation": recommendation.get("recommendation"),
            "reason": recommendation.get("reason"),
        }
    except Exception as e:
        app_logger.error(f"Deal signal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/price-tracker/track")
async def track_price_change(req: TrackRequest):
    """Track a price change and auto-generate alerts for big drops"""
    try:
        # 1. Resolve Product ID (search by name or canonical)
        product_res = supabase_db.table('products').select('id').ilike('name', f"%{req.product_name}%").limit(1).execute()
        product_id = product_res.data[0]['id'] if product_res.data else req.product_name
        
        # 2. Resolve Platform ID
        platform_res = supabase_db.table('platforms').select('id').ilike('name', f"%{req.platform}%").limit(1).execute()
        platform_id = platform_res.data[0]['id'] if platform_res.data else req.platform
        
        # Convert price to float safely
        try:
            val_price = float(req.price.replace(',', '').replace('₹', '').strip())
        except:
            val_price = 0.0

        price_change = PriceTracker.track_price_change(product_id, platform_id, val_price)
        alert_created = False
        if price_change and price_change['change_percent'] > 5:
            try:
                supabase_db.table('price_alerts').insert({
                    'user_id': req.user_id,
                    'alert_type': 'price_drop',
                    'previous_price': price_change['previous_price'],
                    'new_price': price_change['new_price'],
                    'price_drop_amount': price_change['change_amount'],
                    'price_drop_percent': price_change['change_percent'],
                    'product_url': req.url,
                    'product_name': req.product_name,
                    'platform_name': req.platform,
                }).execute()
                alert_created = True
            except Exception as alert_err:
                app_logger.warning(f"Alert creation failed: {alert_err}")
        return {"success": True, "price_change": price_change, "alert_created": alert_created}
    except Exception as e:
        app_logger.error(f"Track price error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ MERGED — RECOMMENDATIONS ====================

@app.get("/api/recommendations/personalized")
async def get_personalized_recommendations(user_id: str):
    """Personalized product recommendations"""
    try:
        rec = RecommendationEngine.generate_recommendations(user_id)
        RecommendationEngine.save_recommendation(rec)
        return rec.model_dump()
    except Exception as e:
        app_logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/browsing-history")
async def get_browsing_history(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
):
    """User browsing history"""
    try:
        return {"items": RecommendationEngine.get_user_browsing_history(user_id, limit)}
    except Exception as e:
        app_logger.error(f"Browsing history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/category-trends")
async def get_category_trends(
    category: str,
    limit: int = Query(10, ge=1, le=50),
):
    """Trending products in a category"""
    try:
        return {"trends": RecommendationEngine.get_category_trends(category, limit)}
    except Exception as e:
        app_logger.error(f"Category trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ALERT CRUD (direct Supabase queries) ====================

@app.get("/api/alerts/user")
async def get_user_alerts_list(
    user_id: str,
    unread_only: bool = False,
):
    """Get alerts for a user"""
    try:
        query = supabase_db.table('price_alerts').select('*').eq('user_id', user_id)
        if unread_only:
            query = query.eq('notification_sent', False)
        result = query.order('created_at', desc=True).limit(50).execute()
        return {"alerts": result.data or []}
    except Exception as e:
        app_logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """Mark alert as read"""
    try:
        supabase_db.table('price_alerts').update(
            {'notification_sent': True}
        ).eq('id', alert_id).execute()
        return {"success": True}
    except Exception as e:
        app_logger.error(f"Mark alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    try:
        supabase_db.table('price_alerts').delete().eq('id', alert_id).execute()
        return {"success": True}
    except Exception as e:
        app_logger.error(f"Delete alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ERROR HANDLER ====================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all error handler"""
    app_logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ============ SCHEDULER STARTUP/SHUTDOWN ============

@app.on_event("startup")
async def startup_event():
    """Initialize background scheduler on app startup"""
    try:
        from utils.scheduler import start_background_scheduler
        start_background_scheduler()
        app_logger.info("✅ Background scheduler initialized on startup")
    except Exception as e:
        app_logger.error(f"⚠️ Failed to start scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on app shutdown"""
    try:
        from utils.scheduler import stop_background_scheduler
        stop_background_scheduler()
        app_logger.info("✅ Background scheduler stopped on shutdown")
    except Exception as e:
        app_logger.error(f"⚠️ Failed to stop scheduler: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )