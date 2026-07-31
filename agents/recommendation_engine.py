"""
AI Recommendation Engine
Generates personalized product and bundle recommendations
"""
from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import app_logger
from utils.supabase_client import db as supabase_db
from utils.affiliate_url_generator import build_purchase_links
from pydantic import BaseModel
from agents.price_tracker import PriceTracker

class RecommendationItem(BaseModel):
    product_id: str
    product_name: str
    reason: str
    score: float
    current_price: Optional[float]
    discount_available: bool
    buy_url: Optional[str] = None
    affiliate_url: Optional[str] = None
    affiliate_enabled: bool = False

class Recommendation(BaseModel):
    user_id: str
    timestamp: str
    recommendations: List[RecommendationItem]
    bundle_suggestions: List[Dict]

class RecommendationEngine:
    """Generate personalized product recommendations"""

    @staticmethod
    def get_purchase_links(product_id: str) -> Dict:
        """Return direct and affiliate URLs for a product.

        Affiliate URL is only included when the corresponding env token exists.
        """
        try:
            result = supabase_db.table('product_prices')\
                .select('product_url, platform_id, price, in_stock')\
                .eq('product_id', product_id)\
                .eq('in_stock', True)\
                .order('price', desc=False)\
                .limit(1)\
                .execute()

            if not result.data:
                return {
                    'buy_url': None,
                    'affiliate_url': None,
                    'affiliate_enabled': False,
                    'platform': 'unknown',
                }

            row = result.data[0]
            product_url = row.get('product_url')
            platform_hint = row.get('platform_id')

            if not product_url:
                return {
                    'buy_url': None,
                    'affiliate_url': None,
                    'affiliate_enabled': False,
                    'platform': 'unknown',
                }

            return build_purchase_links(
                product_url=product_url,
                platform_hint=platform_hint,
            )
        except Exception as e:
            app_logger.error(f"Error getting purchase links: {e}")
            return {
                'buy_url': None,
                'affiliate_url': None,
                'affiliate_enabled': False,
                'platform': 'unknown',
            }

    @staticmethod
    def get_best_buy_url(product_id: str) -> Optional[str]:
        """Return the lowest in-stock product URL for direct purchase."""
        links = RecommendationEngine.get_purchase_links(product_id)
        return links.get('buy_url')
    
    @staticmethod
    def get_user_browsing_history(user_id: str, limit: int = 20) -> List[Dict]:
        """Get products user has viewed"""
        try:
            result = supabase_db.table('browsing_history')\
                .select('product_id, products(id, name, category, avg_rating)')\
                .eq('user_id', user_id)\
                .order('viewed_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return [item['products'] for item in result.data if item.get('products')]
        except Exception as e:
            app_logger.error(f"Error fetching browsing history: {e}")
            return []
    
    @staticmethod
    def get_user_wishlist(user_id: str) -> List[Dict]:
        """Get user's wishlist items"""
        try:
            result = supabase_db.table('wishlists')\
                .select('product_id, products(id, name, category, avg_rating, min_price)')\
                .eq('user_id', user_id)\
                .eq('is_active', True)\
                .execute()
            
            return [item['products'] for item in result.data if item.get('products')]
        except Exception as e:
            app_logger.error(f"Error fetching wishlist: {e}")
            return []
    
    @staticmethod
    def get_category_trends(category: str, limit: int = 10) -> List[Dict]:
        """Get trending products in a category"""
        try:
            result = supabase_db.table('products')\
                .select('id, name, avg_rating, view_count, min_price')\
                .eq('category', category)\
                .order('view_count', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data or []
        except Exception as e:
            app_logger.error(f"Error fetching category trends: {e}")
            return []
    
    @staticmethod
    def generate_recommendations(user_id: str) -> Recommendation:
        """Generate personalized recommendations for user"""
        try:
            recommendations = []
            
            # Get user's browsing history and interests
            browsed = RecommendationEngine.get_user_browsing_history(user_id)
            wishlist = RecommendationEngine.get_user_wishlist(user_id)
            
            # Find price drops in wishlist
            for item in wishlist:
                try:
                    price_insight = PriceTracker.should_buy_now(item['id'])
                    
                    if price_insight.get('recommendation') in ['buy_now']:
                        links = RecommendationEngine.get_purchase_links(item['id'])
                        rec = RecommendationItem(
                            product_id=item['id'],
                            product_name=item['name'],
                            reason=f"Wishlist item on sale: {price_insight.get('reason', '')}",
                            score=0.95,
                            current_price=price_insight.get('current_price'),
                            discount_available=True,
                            buy_url=links.get('buy_url'),
                            affiliate_url=links.get('affiliate_url'),
                            affiliate_enabled=bool(links.get('affiliate_enabled', False))
                        )
                        recommendations.append(rec)
                except:
                    pass
            
            # Get category-based recommendations from browsing history
            categories = set()
            for item in browsed[:5]:
                if item.get('category'):
                    categories.add(item['category'])
            
            for category in categories:
                trends = RecommendationEngine.get_category_trends(category, limit=3)
                for trend in trends:
                    # Skip if already in wishlist
                    if any(w['id'] == trend['id'] for w in wishlist):
                        continue

                    links = RecommendationEngine.get_purchase_links(trend['id'])
                    
                    rec = RecommendationItem(
                        product_id=trend['id'],
                        product_name=trend['name'],
                        reason=f"Trending in {category} (⭐ {trend.get('avg_rating', 0):.1f})",
                        score=0.75 + (trend.get('avg_rating', 0) / 5.0) * 0.15,
                        current_price=trend.get('min_price'),
                        discount_available=False,
                        buy_url=links.get('buy_url'),
                        affiliate_url=links.get('affiliate_url'),
                        affiliate_enabled=bool(links.get('affiliate_enabled', False))
                    )
                    recommendations.append(rec)
            
            # Bundle suggestions (products frequently bought together)
            bundle_suggestions = []
            if recommendations:
                first_product = recommendations[0].product_id
                try:
                    bundle_result = supabase_db.table('purchase_history')\
                        .select('product_id')\
                        .eq('purchased_with_product', first_product)\
                        .limit(3)\
                        .execute()
                    
                    bundle_items = [b['product_id'] for b in bundle_result.data or []]
                    if bundle_items:
                        bundle_suggestions.append({
                            'main_product': first_product,
                            'bundle_with': bundle_items,
                            'savings_percentage': 10
                        })
                except:
                    pass
            
            # Sort by score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return Recommendation(
                user_id=user_id,
                timestamp=datetime.now().isoformat(),
                recommendations=recommendations[:10],  # Top 10
                bundle_suggestions=bundle_suggestions
            )
            
        except Exception as e:
            app_logger.error(f"Error generating recommendations: {e}")
            return Recommendation(
                user_id=user_id,
                timestamp=datetime.now().isoformat(),
                recommendations=[],
                bundle_suggestions=[]
            )
    
    @staticmethod
    def save_recommendation(recommendation: Recommendation) -> bool:
        """Save recommendation to database for history"""
        try:
            supabase_db.table('recommendations').insert({
                'user_id': recommendation.user_id,
                'data': {
                    'items': [r.dict() for r in recommendation.recommendations],
                    'bundles': recommendation.bundle_suggestions
                },
                'created_at': recommendation.timestamp
            }).execute()
            
            return True
        except Exception as e:
            app_logger.error(f"Error saving recommendation: {e}")
            return False
