from dotenv import load_dotenv
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.product_finder import run_product_finder
from agents.price_historian import run_price_historian
from agents.market_analyzer import run_market_analyzer
from agents.ai_predictor import run_ai_predictor
from agents.alert_manager import run_alert_manager

load_dotenv()

# ── STATE (the backpack) ──────────────────────────
class PriceAgentState(TypedDict):
    # User inputs
    product_name: str
    user_email: str

    # Agent 1 outputs
    products_found: list
    best_5_products: list
    all_products: list
    alternatives_found: list
    search_query: str
    total_found: int

    # Agent 2 outputs
    price_history: list
    best_price_data: list

    # Agent 3 outputs
    upcoming_sales: list
    product_deals: list

    # Agent 4 outputs
    ai_prediction: str

    # Agent 5 outputs
    alert_status: str

# ── BUILD THE GRAPH ───────────────────────────────
def build_pipeline():
    graph = StateGraph(PriceAgentState)

    # Add all 5 agent nodes
    graph.add_node("product_finder", run_product_finder)
    graph.add_node("price_historian", run_price_historian)
    graph.add_node("market_analyzer", run_market_analyzer)
    graph.add_node("ai_predictor", run_ai_predictor)
    graph.add_node("alert_manager", run_alert_manager)

    # Set entry point
    graph.set_entry_point("product_finder")

    # Simple straight edges
    graph.add_edge("product_finder", "price_historian")
    graph.add_edge("price_historian", "market_analyzer")
    graph.add_edge("market_analyzer", "ai_predictor")
    graph.add_edge("ai_predictor", "alert_manager")
    graph.add_edge("alert_manager", END)

    return graph.compile()

# ── RUN FUNCTION ──────────────────────────────────
def run_price_pipeline(product_name: str, user_email: str) -> dict:
    pipeline = build_pipeline()

    result = pipeline.invoke({
        "product_name": product_name,
        "user_email": user_email,
        "products_found": [],
        "best_5_products": [],
        "all_products": [],
        "alternatives_found": [],
        "search_query": "",
        "total_found": 0,
        "price_history": [],
        "best_price_data": [],
        "upcoming_sales": [],
        "product_deals": [],
        "ai_prediction": "",
        "alert_status": ""
    })

    return result


if __name__ == "__main__":
    import sys
    import json
    
    # Simple CLI for testing the pipeline
    test_product = sys.argv[1] if len(sys.argv) > 1 else "iphone 14 pro"
    test_email = sys.argv[2] if len(sys.argv) > 2 else "admin@smartshop.ai"
    
    print(f"\n🚀 Starting Price Intelligence Pipeline for: {test_product}")
    print(f"📧 User Email: {test_email}\n")
    
    try:
        final_state = run_price_pipeline(test_product, test_email)
        
        print("\n✅ Pipeline complete! Results summary:")
        print(f"   - Products Found: {len(final_state.get('products_found', []))}")
        print(f"   - Best Price: ₹{final_state.get('best_5_products', [{}])[0].get('price', 'N/A')}")
        print(f"   - AI Prediction: {final_state.get('ai_prediction', 'N/A')[:100]}...")
        print(f"   - Alert Status: {final_state.get('alert_status')}\n")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        sys.exit(1)