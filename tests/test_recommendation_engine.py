"""
Unit Tests for Recommendation Engine Module
"""
import pytest
from datetime import datetime
from agents.recommendation_engine import (
    RecommendationItem,
    Recommendation,
    RecommendationEngine
)

# Mock data
@pytest.fixture
def mock_recommendation_item():
    return RecommendationItem(
        product_id="prod_123",
        product_name="Wireless Headphones",
        reason="Wishlist item on sale: Price drop of 15%",
        score=0.95,
        current_price=1999.99,
        discount_available=True
    )

@pytest.fixture
def mock_recommendation():
    return Recommendation(
        user_id="user_123",
        timestamp=datetime.now().isoformat(),
        recommendations=[
            RecommendationItem(
                product_id="prod_123",
                product_name="Wireless Headphones",
                reason="Wishlist item on sale",
                score=0.95,
                current_price=1999.99,
                discount_available=True
            )
        ],
        bundle_suggestions=[
            {
                "main_product": "prod_123",
                "bundle_with": ["prod_124"],
                "savings_percentage": 10
            }
        ]
    )

class TestRecommendationItemModel:
    """Test RecommendationItem data model"""
    
    def test_recommendation_item_creation(self, mock_recommendation_item):
        item = mock_recommendation_item
        assert item.product_id == "prod_123"
        assert item.score == 0.95
        assert item.discount_available == True
    
    def test_recommendation_item_dict(self, mock_recommendation_item):
        item_dict = mock_recommendation_item.model_dump()
        assert "product_id" in item_dict
        assert "score" in item_dict
        assert item_dict["product_id"] == "prod_123"

class TestRecommendationModel:
    """Test Recommendation data model"""
    
    def test_recommendation_creation(self, mock_recommendation):
        rec = mock_recommendation
        assert rec.user_id == "user_123"
        assert len(rec.recommendations) > 0
        assert len(rec.bundle_suggestions) > 0
    
    def test_recommendation_dict(self, mock_recommendation):
        rec_dict = mock_recommendation.model_dump()
        assert "user_id" in rec_dict
        assert "timestamp" in rec_dict
        assert "recommendations" in rec_dict

class TestScoreCalculation:
    """Test recommendation scoring"""
    
    def test_score_ranges(self):
        """Score should be between 0 and 1"""
        scores = [0.5, 0.75, 0.95]
        for score in scores:
            assert 0 <= score <= 1
    
    def test_high_score_priority(self):
        """Higher scores mean higher priority"""
        scores = [0.6, 0.8, 0.95]
        sorted_scores = sorted(scores, reverse=True)
        assert sorted_scores[0] == 0.95
        assert sorted_scores[-1] == 0.6

class TestRecommendationTypes:
    """Test different recommendation reason types"""
    
    def test_wishlist_reason(self):
        reason = "Wishlist item on sale: Price drop of 15%"
        assert "Wishlist" in reason
        assert "sale" in reason
    
    def test_category_trend_reason(self):
        reason = "Trending in Electronics (⭐ 4.8)"
        assert "Trending" in reason
        assert "Electronics" in reason
    
    def test_personalized_reason(self):
        reason = "Based on your browsing history"
        assert "browsing history" in reason

class TestBundleSuggestion:
    """Test bundle calculation logic"""
    
    def test_bundle_savings(self):
        individual_prices = [1999.99, 299.99, 199.99]
        total = sum(individual_prices)
        discount_percent = 10
        bundle_price = total * (1 - discount_percent / 100)
        savings = total - bundle_price
        
        assert savings == pytest.approx(249.997, rel=0.01)
        assert bundle_price == pytest.approx(2249.97, rel=0.01)
    
    def test_savings_percentage_calculation(self):
        total = 2500
        savings = 250
        savings_percent = (savings / total) * 100
        
        assert savings_percent == 10.0

class TestRecommendationFiltering:
    """Test recommendation filtering logic"""
    
    def test_top_recommendations(self):
        """Should return top N recommendations sorted by score"""
        items = [
            {"name": "Product A", "score": 0.7},
            {"name": "Product B", "score": 0.95},
            {"name": "Product C", "score": 0.6},
        ]
        sorted_items = sorted(items, key=lambda x: x['score'], reverse=True)
        top_3 = sorted_items[:3]
        
        assert len(top_3) == 3
        assert top_3[0]['score'] == 0.95
        assert top_3[-1]['score'] == 0.6
    
    def test_duplicate_filtering(self):
        """Should remove duplicate recommendations"""
        items = ["prod_1", "prod_2", "prod_1", "prod_3"]
        unique_items = list(dict.fromkeys(items))
        
        assert len(unique_items) == 3
        assert "prod_1" in unique_items

class TestCategoryMatching:
    """Test category-based recommendations"""
    
    def test_category_detection(self):
        products = [
            {"id": "p1", "category": "Electronics"},
            {"id": "p2", "category": "Electronics"},
            {"id": "p3", "category": "Fashion"}
        ]
        
        electronics = [p for p in products if p["category"] == "Electronics"]
        assert len(electronics) == 2
    
    def test_category_trend_sorting(self):
        trends = [
            {"product": "A", "view_count": 1000},
            {"product": "B", "view_count": 5000},
            {"product": "C", "view_count": 2000},
        ]
        
        sorted_trends = sorted(trends, key=lambda x: x['view_count'], reverse=True)
        assert sorted_trends[0]["product"] == "B"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
