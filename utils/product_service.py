"""
Product Models and Multi-Platform Search Service
Handles product data, aggregation, and searching across platforms
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from utils.logger import app_logger
from utils.supabase_client import db as supabase_db
import hashlib
from fastapi import HTTPException

# ==================== PRODUCT MODELS ====================

class ProductPrice(BaseModel):
    platform_id: str
    platform_name: str
    price: float
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    in_stock: bool
    product_url: str
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    last_checked: datetime

class ProductBase(BaseModel):
    name: str
    brand: str
    model: Optional[str] = None
    color: Optional[str] = None
    category_id: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    unique_hash: str
    canonical_name: str

class Product(ProductBase):
    id: str
    average_rating: Optional[float] = None
    total_reviews: int = 0
    prices: List[ProductPrice] = []
    best_price: Optional[float] = None
    best_price_platform: Optional[str] = None
    created_at: datetime
    last_updated: datetime

class ProductComparison(BaseModel):
    product_id: str
    product_name: str
    brand: str
    image_url: Optional[str]
    average_rating: Optional[float]
    total_reviews: int
    best_price: float
    best_price_platform: str
    price_options: List[ProductPrice]
    url_amazon: Optional[str] = None
    url_flipkart: Optional[str] = None
    url_croma: Optional[str] = None

class SearchResponse(BaseModel):
    total_results: int
    products: List[ProductComparison]

# ==================== PRODUCT SERVICE ====================

def generate_product_hash(name: str, brand: str, model: Optional[str] = None, color: Optional[str] = None) -> str:
    """Generate unique hash for product deduplication"""
    key = f"{name.lower()}-{brand.lower()}-{model or ''}-{color or ''}"
    return hashlib.md5(key.encode()).hexdigest()

def generate_canonical_name(name: str, brand: str) -> str:
    """Generate canonical product name for normalization"""
    # Remove common words and standardize format
    common_words = ['pro', 'plus', 'max', 'ultra', 'lite', 'version']
    parts = name.lower().split()
    parts = [p for p in parts if p not in common_words]
    return f"{brand.lower()} {' '.join(parts)}".strip()

def get_or_create_product(product_data: ProductCreate) -> str:
    """Get existing product or create new one"""
    try:
        # Check if product already exists by hash
        result = supabase_db.table('products').select('id').eq('unique_hash', product_data.unique_hash).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['id']
        
        # Create new product
        insert_data = product_data.dict()
        result = supabase_db.table('products').insert(insert_data).execute()
        
        if result.data:
            product_id = result.data[0]['id']
            app_logger.info(f"✅ Product created: {product_data.name} ({product_id})")
            return product_id
        
        raise Exception("Failed to create product")
        
    except Exception as e:
        app_logger.error(f"Error getting/creating product: {str(e)}")
        raise

def save_product_price(product_id: str, platform_id: str, price_data: dict):
    """Save product price from a platform"""
    try:
        insert_data = {
            'product_id': product_id,
            'platform_id': platform_id,
            'price': price_data.get('price'),
            'original_price': price_data.get('original_price'),
            'discount_percent': price_data.get('discount_percent'),
            'in_stock': price_data.get('in_stock', True),
            'product_url': price_data.get('product_url'),
            'rating': price_data.get('rating'),
            'reviews_count': price_data.get('reviews_count', 0),
            'scrape_source': price_data.get('scrape_source', 'api')
        }
        
        result = supabase_db.table('product_prices').insert(insert_data).execute()
        
        if result.data:
            app_logger.debug(f"✅ Price saved for product {product_id} on platform {platform_id}")
            return result.data[0]
        
        raise Exception("Failed to save price")
        
    except Exception as e:
        app_logger.error(f"Error saving product price: {str(e)}")
        raise

def get_product_with_prices(product_id: str) -> Product:
    """Get product with all its prices across platforms"""
    try:
        # Get product
        result = supabase_db.table('products').select('*').eq('id', product_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = result.data[0]
        
        # Get all prices
        prices_result = supabase_db.table('product_prices').select(
            'id, platform_id, price, original_price, discount_percent, in_stock, product_url, rating, reviews_count, last_checked, platforms(name)'
        ).eq('product_id', product_id).order('price', desc=False).limit(1, offset=0).execute()
        
        prices = []
        best_price = None
        best_platform = None
        
        for price_record in prices_result.data or []:
            product_price = ProductPrice(
                platform_id=price_record['platform_id'],
                platform_name=price_record.get('platforms', {}).get('name', 'Unknown'),
                price=price_record['price'],
                original_price=price_record.get('original_price'),
                discount_percent=price_record.get('discount_percent'),
                in_stock=price_record['in_stock'],
                product_url=price_record['product_url'],
                rating=price_record.get('rating'),
                reviews_count=price_record.get('reviews_count'),
                last_checked=price_record['last_checked']
            )
            prices.append(product_price)
            
            # Track best price
            if price_record['in_stock'] and (best_price is None or price_record['price'] < best_price):
                best_price = price_record['price']
                best_platform = product_price.platform_name
        
        return Product(
            id=product['id'],
            name=product['name'],
            brand=product.get('brand'),
            model=product.get('model'),
            color=product.get('color'),
            category_id=product.get('category_id'),
            description=product.get('description'),
            image_url=product.get('image_url'),
            average_rating=product.get('average_rating'),
            total_reviews=product.get('total_reviews', 0),
            prices=prices,
            best_price=best_price,
            best_price_platform=best_platform,
            created_at=product['created_at'],
            last_updated=product['last_updated']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting product with prices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get product")

def search_products(query: str, category_id: Optional[str] = None, limit: int = 20) -> SearchResponse:
    """
    Search for products across all platforms
    """
    try:
        # Build query
        search_query = supabase_db.table('products').select(
            '*'
        ).ilike('canonical_name', f"%{query.lower()}%")
        
        if category_id:
            search_query = search_query.eq('category_id', category_id)
        
        search_query = search_query.order('average_rating', desc=True).limit(limit)
        result = search_query.execute()
        
        products = []
        
        for product in result.data or []:
            # Get best prices for this product
            prices_result = supabase_db.table('product_prices').select(
                'platform_id, price, original_price, discount_percent, in_stock, product_url, rating, reviews_count, platforms(name)'
            ).eq('product_id', product['id']).eq('in_stock', True).order('price', desc=False).execute()
            
            price_options = []
            best_price = None
            best_platform = None
            urls = {}
            
            for price_record in prices_result.data or []:
                platform_name = price_record.get('platforms', {}).get('name', 'Unknown')
                platform_id = price_record['platform_id']
                
                # Handle datetime conversion
                now = datetime.now()
                last_checked = now
                
                product_price = ProductPrice(
                    platform_id=platform_id,
                    platform_name=platform_name,
                    price=price_record['price'],
                    original_price=price_record.get('original_price'),
                    discount_percent=price_record.get('discount_percent'),
                    in_stock=True,
                    product_url=price_record['product_url'],
                    rating=price_record.get('rating'),
                    reviews_count=price_record.get('reviews_count'),
                    last_checked=last_checked
                )
                price_options.append(product_price)
                
                # Track best price
                if best_price is None or price_record['price'] < best_price:
                    best_price = price_record['price']
                    best_platform = platform_name
                
                # Store URLs by platform
                platform_slug = platform_name.lower().replace(' ', '_')
                urls[f"url_{platform_slug}"] = price_record['product_url']
            
            if best_price:
                products.append(ProductComparison(
                    product_id=product['id'],
                    product_name=product['name'],
                    brand=product.get('brand', 'Unknown'),
                    image_url=product.get('image_url'),
                    average_rating=product.get('average_rating'),
                    total_reviews=product.get('total_reviews', 0),
                    best_price=best_price,
                    best_price_platform=best_platform,
                    price_options=price_options,
                    **urls
                ))
        
        app_logger.info(f"✅ Search completed: '{query}' - Found {len(products)} products")
        
        return SearchResponse(
            total_results=len(products),
            products=products
        )
        
    except Exception as e:
        app_logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")
