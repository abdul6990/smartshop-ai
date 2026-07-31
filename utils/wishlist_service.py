"""
Wishlist Management
Handle user wishlists, tracking, and price alerts
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from utils.logger import app_logger
from utils.supabase_client import db as supabase_db
from fastapi import HTTPException
import json

# ==================== WISHLIST MODELS ====================

class WishlistItemBase(BaseModel):
    product_id: str
    target_price: Optional[float] = None

class WishlistItemCreate(WishlistItemBase):
    pass

class WishlistItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_image_url: Optional[str]
    product_brand: str
    price_when_added: float
    target_price: Optional[float]
    lowest_price_seen: Optional[float]
    is_purchased: bool
    current_best_price: Optional[float]
    current_best_platform: Optional[str]
    price_drop_count: int
    added_at: datetime
    updated_at: datetime

class WishlistBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class WishlistCreate(WishlistBase):
    pass

class WishlistResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    is_default: bool
    is_public: bool
    item_count: int = 0
    items: List[WishlistItemResponse] = []
    created_at: datetime
    updated_at: datetime

class PriceAlertResponse(BaseModel):
    id: str
    product_name: str
    previous_price: float
    new_price: float
    price_drop_amount: float
    price_drop_percent: float
    platform_name: str
    product_url: str
    created_at: datetime

# ==================== WISHLIST SERVICE ====================

def get_user_wishlists(user_id: str) -> List[WishlistResponse]:
    """Get all wishlists for a user"""
    try:
        result = supabase_db.table('wishlists').select('*').eq('user_id', user_id).execute()
        
        wishlists = []
        for wishlist in result.data or []:
            # Get items count
            items_result = supabase_db.table('wishlist_items').select('id').eq('wishlist_id', wishlist['id']).execute()
            item_count = len(items_result.data or [])
            
            wishlists.append(WishlistResponse(
                id=wishlist['id'],
                user_id=wishlist['user_id'],
                name=wishlist['name'],
                description=wishlist.get('description'),
                is_default=wishlist['is_default'],
                is_public=wishlist['is_public'],
                item_count=item_count,
                created_at=wishlist['created_at'],
                updated_at=wishlist['updated_at']
            ))
        
        return wishlists
        
    except Exception as e:
        app_logger.error(f"Error getting wishlists: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get wishlists")

def get_wishlist_with_items(wishlist_id: str, user_id: str) -> WishlistResponse:
    """Get wishlist with all items"""
    try:
        # Get wishlist
        result = supabase_db.table('wishlists').select('*').eq('id', wishlist_id).eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        wishlist = result.data[0]
        
        # Get items with product details and prices
        items_result = supabase_db.table('wishlist_items').select(
            '*,products(name,image_url,brand)'
        ).eq('wishlist_id', wishlist_id).order('added_at', desc=True).execute()
        
        items = []
        for item in items_result.data or []:
            # Get current best price
            prices_result = supabase_db.table('product_prices').select(
                'price,platform_id,platforms(name)'
            ).eq('product_id', item['product_id']).eq('in_stock', True).order('price', desc=False).limit(1).execute()
            
            best_price = None
            best_platform = None
            if prices_result.data:
                best_price = prices_result.data[0]['price']
                best_platform = prices_result.data[0].get('platforms', {}).get('name')
            
            product_info = item.get('products', {})
            items.append(WishlistItemResponse(
                id=item['id'],
                product_id=item['product_id'],
                product_name=product_info.get('name', 'Unknown'),
                product_image_url=product_info.get('image_url'),
                product_brand=product_info.get('brand', 'Unknown'),
                price_when_added=item['price_when_added'],
                target_price=item.get('target_price'),
                lowest_price_seen=item.get('lowest_price_seen'),
                is_purchased=item['is_purchased'],
                current_best_price=best_price,
                current_best_platform=best_platform,
                price_drop_count=item['price_drop_count'],
                added_at=item['added_at'],
                updated_at=item['updated_at']
            ))
        
        return WishlistResponse(
            id=wishlist['id'],
            user_id=wishlist['user_id'],
            name=wishlist['name'],
            description=wishlist.get('description'),
            is_default=wishlist['is_default'],
            is_public=wishlist['is_public'],
            item_count=len(items),
            items=items,
            created_at=wishlist['created_at'],
            updated_at=wishlist['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting wishlist items: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get wishlist")

def add_to_wishlist(wishlist_id: str, user_id: str, product_id: str, target_price: Optional[float] = None) -> WishlistItemResponse:
    """Add product to wishlist"""
    try:
        # Verify wishlist belongs to user
        wishlist_result = supabase_db.table('wishlists').select('id').eq('id', wishlist_id).eq('user_id', user_id).execute()
        if not wishlist_result.data:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        # Get current best price
        prices_result = supabase_db.table('product_prices').select('price').eq('product_id', product_id).eq('in_stock', True).order('price', desc=False).limit(1).execute()
        
        current_price = None
        if prices_result.data:
            current_price = prices_result.data[0]['price']
        
        # Get product info
        product_result = supabase_db.table('products').select('name,image_url,brand').eq('id', product_id).execute()
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Add to wishlist - ensure all fields are valid types
        insert_data = {
            'wishlist_id': wishlist_id,
            'product_id': product_id,
            'price_when_added': current_price if current_price else 0,
            'target_price': target_price if target_price else 0,
            'lowest_price_seen': current_price if current_price else 0
        }
        
        result = supabase_db.table('wishlist_items').insert(insert_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to add to wishlist")
        
        item = result.data[0]
        product_info = product_result.data[0]
        
        best_platform = None
        
        app_logger.info(f"✅ Product added to wishlist: {product_id}")
        
        return WishlistItemResponse(
            id=item['id'],
            product_id=item['product_id'],
            product_name=product_info['name'],
            product_image_url=product_info.get('image_url'),
            product_brand=product_info.get('brand', 'Unknown'),
            price_when_added=item['price_when_added'],  # Use value from DB, not local variable
            target_price=item['target_price'],          # Use value from DB
            lowest_price_seen=item['lowest_price_seen'], # Use value from DB
            is_purchased=False,
            current_best_price=current_price,
            current_best_platform=best_platform,
            price_drop_count=0,
            added_at=item['added_at'],
            updated_at=item['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error adding to wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add to wishlist")

def remove_from_wishlist(wishlist_item_id: str, user_id: str) -> dict:
    """Remove product from wishlist"""
    try:
        # Verify item belongs to user's wishlist
        item_result = supabase_db.table('wishlist_items').select('wishlist_id').eq('id', wishlist_item_id).execute()
        if not item_result.data:
            raise HTTPException(status_code=404, detail="Wishlist item not found")
        
        wishlist_id = item_result.data[0]['wishlist_id']
        wishlist_result = supabase_db.table('wishlists').select('id').eq('id', wishlist_id).eq('user_id', user_id).execute()
        
        if not wishlist_result.data:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Delete item
        supabase_db.table('wishlist_items').delete().eq('id', wishlist_item_id).execute()
        
        app_logger.info(f"✅ Item removed from wishlist: {wishlist_item_id}")
        
        return {"success": True, "message": "Item removed from wishlist"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error removing from wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove from wishlist")

def mark_item_purchased(wishlist_item_id: str, user_id: str, platform_id: str, purchase_price: float) -> dict:
    """Mark wishlist item as purchased"""
    try:
        # Verify item belongs to user
        item_result = supabase_db.table('wishlist_items').select('wishlist_id,product_id').eq('id', wishlist_item_id).execute()
        if not item_result.data:
            raise HTTPException(status_code=404, detail="Wishlist item not found")
        
        wishlist_id = item_result.data[0]['wishlist_id']
        product_id = item_result.data[0]['product_id']
        
        wishlist_result = supabase_db.table('wishlists').select('id').eq('id', wishlist_id).eq('user_id', user_id).execute()
        if not wishlist_result.data:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Update item as purchased
        supabase_db.table('wishlist_items').update({
            'is_purchased': True,
            'purchase_date': datetime.utcnow().isoformat(),
            'purchase_platform_id': platform_id,
            'purchase_price': purchase_price
        }).eq('id', wishlist_item_id).execute()
        
        # Record purchase
        supabase_db.table('purchases').insert({
            'user_id': user_id,
            'product_id': product_id,
            'platform_id': platform_id,
            'purchase_price': purchase_price
        }).execute()
        
        app_logger.info(f"✅ Item marked as purchased: {wishlist_item_id}")
        
        return {"success": True, "message": "Item marked as purchased"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error marking purchased: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update purchase status")

def get_price_alerts(user_id: str, limit: int = 50) -> List[PriceAlertResponse]:
    """Get price alerts for user's wishlist"""
    try:
        # Get all price alerts for user
        result = supabase_db.table('price_alerts').select(
            '*,wishlist_items(product_id,products(name)),platforms(name)'
        ).eq('user_id', user_id).eq('notification_sent', False).order('created_at', desc=True).limit(limit).execute()
        
        alerts = []
        for alert in result.data or []:
            product_info = alert.get('wishlist_items', {}).get('products', {})
            alerts.append(PriceAlertResponse(
                id=alert['id'],
                product_name=product_info.get('name', 'Unknown'),
                previous_price=alert['previous_price'],
                new_price=alert['new_price'],
                price_drop_amount=alert['price_drop_amount'],
                price_drop_percent=alert['price_drop_percent'],
                platform_name=alert.get('platforms', {}).get('name', 'Unknown'),
                product_url=alert['product_url'],
                created_at=alert['created_at']
            ))
        
        return alerts
        
    except Exception as e:
        app_logger.error(f"Error getting price alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get price alerts")
