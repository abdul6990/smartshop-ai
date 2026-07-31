"""
Price History & Charts Data Manager
Generates chart data for price trends over time
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from statistics import mean, stdev, StatisticsError
from utils.logger import app_logger
from utils.supabase_client import db

class PriceChartManager:
    """Manages price history and chart generation"""
    
    @staticmethod
    def get_price_trend(product_id: int, days: int = 30) -> Dict:
        """
        Get price trend data for a product
        
        Returns:
        {
            'product_id': int,
            'days': int,
            'min_price': float,
            'max_price': float,
            'avg_price': float,
            'trend': 'up' | 'down' | 'stable',
            'change_percent': float,
            'data_points': [
                {'date': '2024-01-15', 'price': 4599, 'platform': 'Amazon'},
                ...
            ]
        }
        """
        try:
            # Get price history
            history = db.get_price_history(product_id)
            
            if not history:
                return {
                    'product_id': product_id,
                    'days': days,
                    'status': 'no_data',
                    'message': 'No price history available'
                }
            
            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            sorted_history = sorted(
                history,
                key=lambda x: x['recorded_at']
            )
            
            filtered_data = [
                item for item in sorted_history
                if datetime.fromisoformat(item['recorded_at']) >= cutoff_date
            ]
            
            if not filtered_data:
                return {
                    'product_id': product_id,
                    'days': days,
                    'status': 'no_data',
                    'message': f'No data for last {days} days'
                }
            
            # Extract prices
            prices = [float(item['price'].replace('₹', '').replace(',', '')) 
                     for item in filtered_data]
            
            # Calculate statistics
            min_price = min(prices)
            max_price = max(prices)
            avg_price = mean(prices)
            
            # Calculate trend
            if len(prices) >= 2:
                first_price = prices[0]
                last_price = prices[-1]
                change_percent = ((last_price - first_price) / first_price) * 100
                
                if change_percent > 2:
                    trend = 'up'
                elif change_percent < -2:
                    trend = 'down'
                else:
                    trend = 'stable'
            else:
                change_percent = 0
                trend = 'stable'
            
            # Format data points
            data_points = [
                {
                    'date': item['recorded_at'].split('T')[0],
                    'price': float(item['price'].replace('₹', '').replace(',', '')),
                    'platform': item.get('platform', 'unknown')
                }
                for item in filtered_data
            ]
            
            return {
                'product_id': product_id,
                'days': days,
                'status': 'success',
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'avg_price': round(avg_price, 2),
                'trend': trend,
                'change_percent': round(change_percent, 2),
                'data_points': data_points,
                'point_count': len(data_points)
            }
        
        except Exception as e:
            app_logger.error(f"Failed to get price trend: {e}")
            return {
                'product_id': product_id,
                'status': 'error',
                'message': str(e)
            }
    
    @staticmethod
    def get_best_price_day(product_id: int, days: int = 30) -> Optional[Dict]:
        """Get the day with lowest price"""
        trend = PriceChartManager.get_price_trend(product_id, days)
        
        if trend.get('status') != 'success' or not trend.get('data_points'):
            return None
        
        data_points = trend['data_points']
        best_point = min(data_points, key=lambda x: x['price'])
        
        return {
            'date': best_point['date'],
            'price': best_point['price'],
            'platform': best_point['platform'],
            'savings': round(trend['max_price'] - best_point['price'], 2)
        }
    
    @staticmethod
    def get_price_prediction(product_id: int) -> Dict:
        """
        Simple price prediction based on trend
        Returns predicted price for next 7 days
        """
        try:
            trend = PriceChartManager.get_price_trend(product_id, days=30)
            
            if trend.get('status') != 'success':
                return {'status': 'no_data'}
            
            prices = [p['price'] for p in trend['data_points']]
            
            if len(prices) < 2:
                return {
                    'status': 'insufficient_data',
                    'message': 'Need at least 2 price points'
                }
            
            # Simple linear trend
            avg_price = mean(prices)
            try:
                std_dev = stdev(prices)
            except StatisticsError:
                std_dev = 0
            
            # Predict next 7 days
            if trend['trend'] == 'up':
                predicted_price = avg_price + (std_dev * 0.5)
                confidence = 'low' if std_dev > avg_price * 0.3 else 'high'
            elif trend['trend'] == 'down':
                predicted_price = avg_price - (std_dev * 0.5)
                confidence = 'low' if std_dev > avg_price * 0.3 else 'high'
            else:
                predicted_price = avg_price
                confidence = 'high'
            
            return {
                'status': 'success',
                'current_avg': round(avg_price, 2),
                'predicted_price': round(predicted_price, 2),
                'trend': trend['trend'],
                'confidence': confidence,
                'recommendation': PriceChartManager._get_recommendation(
                    trend['trend'], 
                    trend['change_percent']
                )
            }
        
        except Exception as e:
            app_logger.error(f"Price prediction failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _get_recommendation(trend: str, change_percent: float) -> str:
        """Get buying recommendation based on trend"""
        if trend == 'down' and change_percent < -5:
            return "🔥 Great time to buy - Price dropping!"
        elif trend == 'up' and change_percent > 5:
            return "⏸️ Wait - Price is increasing"
        elif trend == 'stable':
            return "➡️ Price stable - Average time to buy"
        else:
            return "📊 Monitor price trends"
    
    @staticmethod
    def get_savings_summary(user_id: str) -> Dict:
        """
        Get total savings for all tracked products
        """
        try:
            from utils.supabase_client import db as supabase_db
            
            tracked = supabase_db.get_tracked_products(user_id)
            
            total_savings = 0
            total_difference = 0
            products_with_data = 0
            
            for product in tracked:
                trend = PriceChartManager.get_price_trend(product['id'])
                
                if trend.get('status') == 'success':
                    max_price = trend['max_price']
                    min_price = trend['min_price']
                    diff = max_price - min_price
                    
                    if diff > 0:
                        total_savings += diff
                        products_with_data += 1
            
            return {
                'status': 'success',
                'total_potential_savings': round(total_savings, 2),
                'products_tracked': len(tracked),
                'products_with_history': products_with_data,
                'avg_savings_per_product': round(
                    total_savings / products_with_data, 2
                ) if products_with_data > 0 else 0
            }
        
        except Exception as e:
            app_logger.error(f"Savings summary failed: {e}")
            return {'status': 'error', 'message': str(e)}
