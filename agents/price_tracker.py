"""
Price Tracking and History Management
Monitors price changes and generates alerts
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.logger import app_logger
from utils.supabase_client import db as supabase_db
from pydantic import BaseModel
from agents.deal_signal import evaluate_from_history

class PriceHistory(BaseModel):
    date: str
    price: float
    platform: str
    
class PriceAnalysis(BaseModel):
    product_id: str
    current_price: float
    lowest_price: float
    highest_price: float
    average_price: float
    price_trend: str  # "down", "up", "stable"
    days_tracked: int
    history: List[PriceHistory]
    deal_signal: Optional[str] = None
    deal_score: Optional[float] = None

class PriceTracker:
    """Track price changes and generate alerts"""
    
    @staticmethod
    def track_price_change(product_id: str, platform_id: str, new_price: float) -> Optional[Dict]:
        """Track a price change for analytics"""
        try:
            # Get previous price
            prev_result = supabase_db.table('product_prices')\
                .select('price')\
                .eq('product_id', product_id)\
                .eq('platform_id', platform_id)\
                .order('last_checked', desc=True)\
                .limit(1)\
                .execute()
            
            if not prev_result.data:
                app_logger.debug(f"No previous price for {product_id}")
                return None
            
            prev_price = prev_result.data[0]['price']
            price_change = new_price - prev_price
            change_percent = (price_change / prev_price * 100) if prev_price > 0 else 0
            
            if price_change < 0:  # Price dropped
                app_logger.info(f"📉 Price drop for {product_id}: {prev_price} → {new_price} ({change_percent:.1f}%)")
                return {
                    'product_id': product_id,
                    'platform_id': platform_id,
                    'previous_price': prev_price,
                    'new_price': new_price,
                    'change_amount': abs(price_change),
                    'change_percent': abs(change_percent),
                    'is_drop': True
                }
            elif price_change > 0:
                app_logger.info(f"📈 Price increase for {product_id}: {prev_price} → {new_price} ({change_percent:.1f}%)")
            
            return None
            
        except Exception as e:
            app_logger.error(f"Error tracking price change: {e}")
            return None
    
    @staticmethod
    def get_price_history(product_id: str, days: int = 30) -> PriceAnalysis:
        """Get price history and analysis for a product"""
        try:
            # Get price records from last N days
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            prices_result = supabase_db.table('product_prices')\
                .select('price, last_checked, platforms(name)')\
                .eq('product_id', product_id)\
                .gte('last_checked', date_threshold)\
                .order('last_checked', desc=False)\
                .execute()
            
            if not prices_result.data:
                raise Exception("No price history found")
            
            prices = [p['price'] for p in prices_result.data]
            history = [
                PriceHistory(
                    date=p['last_checked'][:10],
                    price=p['price'],
                    platform=p.get('platforms', {}).get('name', 'Unknown')
                )
                for p in prices_result.data
            ]
            
            current_price = prices[-1]
            lowest_price = min(prices)
            highest_price = max(prices)
            average_price = sum(prices) / len(prices)
            deal_info = evaluate_from_history(prices)
            
            # Determine trend
            if current_price < average_price * 0.95:
                trend = "down"
            elif current_price > average_price * 1.05:
                trend = "up"
            else:
                trend = "stable"
            
            return PriceAnalysis(
                product_id=product_id,
                current_price=current_price,
                lowest_price=lowest_price,
                highest_price=highest_price,
                average_price=round(average_price, 2),
                price_trend=trend,
                days_tracked=len(prices_result.data),
                history=history,
                deal_signal=deal_info.get("label"),
                deal_score=deal_info.get("score"),
            )
            
        except Exception as e:
            app_logger.error(f"Error getting price history: {e}")
            raise

    @staticmethod
    def should_buy_now(product_id: str) -> Dict:
        """AI recommendation: should user buy now?"""
        try:
            analysis = PriceTracker.get_price_history(product_id, days=30)
            deal_info = evaluate_from_history([item.price for item in analysis.history])
            deal_label = deal_info.get("label", "NORMAL")
            
            # Decision logic
            if deal_label == "FAKE_DISCOUNT":
                recommendation = "wait"
                reason = "Price pattern indicates likely fake discount; wait for stable pricing"
                confidence = 0.9
            elif deal_label == "GENUINE_BARGAIN":
                recommendation = "buy_now"
                reason = "Detected genuine bargain based on 30-day history"
                confidence = 0.96
            elif analysis.current_price <= analysis.lowest_price * 1.05:
                recommendation = "buy_now"
                reason = f"Current price ₹{analysis.current_price:.0f} is near lowest ₹{analysis.lowest_price:.0f}"
                confidence = 0.95
            elif analysis.current_price <= analysis.average_price * 0.9:
                recommendation = "buy_now"
                reason = f"Price is 10% below average"
                confidence = 0.85
            elif analysis.price_trend == "up":
                recommendation = "buy_now"
                reason = "Prices trending upward, buy before they go higher"
                confidence = 0.75
            elif analysis.price_trend == "down":
                recommendation = "wait_few_days"
                reason = "Prices dropping, wait a few days"
                wait_days = 3
                confidence = 0.70
            else:
                recommendation = "wait"
                reason = "Stable prices, no urgency"
                wait_days = 7
                confidence = 0.60
            
            return {
                "product_id": product_id,
                "recommendation": recommendation,
                "reason": reason,
                "confidence": confidence,
                "current_price": analysis.current_price,
                "wait_days": wait_days if "wait" in recommendation else 0,
                "deal_signal": deal_label,
                "deal_score": deal_info.get("score", 0.0),
                "deal_message": deal_info.get("message", "")
            }
            
        except Exception as e:
            app_logger.error(f"Error generating recommendation: {e}")
            return {
                "recommendation": "buy_now",
                "reason": "Unable to analyze price history",
                "confidence": 0.5
            }
