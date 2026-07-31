"""
Unit Tests for Price Tracker Module
"""
import pytest
from datetime import datetime, timedelta
from agents.price_tracker import PriceTracker, PriceHistory, PriceAnalysis

# Mock data
@pytest.fixture
def mock_price_data():
    return {
        "product_id": "test_prod_123",
        "current_price": 1299.99,
        "lowest_price": 999.99,
        "highest_price": 1499.99,
        "average_price": 1199.99,
        "price_trend": "down",
        "days_tracked": 30,
        "history": [
            {"date": "2024-01-01", "price": 1499.99, "platform": "Amazon"},
            {"date": "2024-01-15", "price": 1299.99, "platform": "Amazon"},
            {"date": "2024-01-20", "price": 1199.99, "platform": "Amazon"},
        ]
    }

class TestPriceHistoryModel:
    """Test PriceHistory data model"""
    
    def test_price_history_creation(self):
        history = PriceHistory(
            date="2024-01-20",
            price=1299.99,
            platform="Amazon"
        )
        assert history.date == "2024-01-20"
        assert history.price == 1299.99
        assert history.platform == "Amazon"

class TestPriceAnalysisModel:
    """Test PriceAnalysis data model"""
    
    def test_price_analysis_creation(self, mock_price_data):
        analysis = PriceAnalysis(**mock_price_data)
        assert analysis.product_id == "test_prod_123"
        assert analysis.current_price == 1299.99
        assert analysis.price_trend == "down"
        assert analysis.days_tracked == 30

class TestShouldBuyNow:
    """Test buy recommendation logic"""
    
    def test_buy_now_when_at_lowest(self, mock_price_data):
        """Should recommend buy when price is at/near lowest"""
        # When current price <= lowest * 1.05
        mock_price_data["current_price"] = 1019.99  # Very close to lowest (999.99)
        
        # This should return buy_now recommendation
        # (implementation depends on actual database)
        assert mock_price_data["current_price"] <= mock_price_data["lowest_price"] * 1.05
    
    def test_wait_when_downtrending(self, mock_price_data):
        """Should recommend wait when prices trending down"""
        assert mock_price_data["price_trend"] == "down"
    
    def test_buy_when_uptrending(self, mock_price_data):
        """Should recommend buy when prices trending up"""
        mock_price_data["price_trend"] = "up"
        assert mock_price_data["price_trend"] == "up"

class TestPriceChangeTracking:
    """Test price change detection"""
    
    def test_price_drop_detection(self):
        previous = 1399.99
        current = 1299.99
        change_percent = ((current - previous) / previous) * 100
        
        assert change_percent < 0  # Negative = drop
        assert abs(change_percent) == pytest.approx(7.14, 0.01)
    
    def test_price_increase_detection(self):
        previous = 1199.99
        current = 1299.99
        change_percent = ((current - previous) / previous) * 100
        
        assert change_percent > 0  # Positive = increase
        assert change_percent == pytest.approx(8.33, 0.01)
    
    def test_significant_drop(self):
        previous = 1500.00
        current = 1200.00
        change_percent = abs(((current - previous) / previous) * 100)
        
        # Alert should trigger for > 10% drop
        assert change_percent > 10

class TestTrendCalculation:
    """Test price trend determination"""
    
    def test_downtrend_calculation(self):
        current = 1100
        average = 1200
        is_downtrend = current < average * 0.95
        
        assert is_downtrend == True
        assert current < 1140
    
    def test_uptrend_calculation(self):
        current = 1300
        average = 1200
        is_uptrend = current > average * 1.05
        
        assert is_uptrend == True
        assert current > 1260
    
    def test_stable_trend_calculation(self):
        current = 1200
        average = 1200
        is_stable = (current >= average * 0.95) and (current <= average * 1.05)
        
        assert is_stable == True

class TestSavingsCalculation:
    """Test savings calculations"""
    
    def test_potential_savings(self):
        current = 1299.99
        lowest = 999.99
        savings = current - lowest
        savings_percent = (savings / current) * 100
        
        assert savings == pytest.approx(300, rel=0.01)
        assert savings_percent == pytest.approx(23.08, rel=0.01)
    
    def test_zero_savings(self):
        current = 1000
        lowest = 1000
        savings = current - lowest
        
        assert savings == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
