"""
Agent 4: AI Predictor
Uses Cohere LLM to analyze data and provide recommendations
"""
from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, SystemMessage
from utils.logger import app_logger
import os

def run_ai_predictor(state: dict) -> dict:
    """
    Agent 4: AI Predictor
    Analyzes all data and provides buy/wait recommendation
    """
    try:
        product_name = state.get("product_name", "").strip()
        
        if not product_name:
            app_logger.warning("Agent 4: No product name provided")
            return {
                "ai_prediction": "Unable to analyze: No product data",
                "error": "No product name"
            }
        
        app_logger.info(f"Agent 4: Analyzing data for '{product_name}'")

        model_name = os.getenv("COHERE_MODEL_NAME", "command-r-plus-08-2024")
        
        llm = ChatCohere(
            cohere_api_key=os.getenv("COHERE_API_KEY"),
            model=model_name
        )
        
        # Compile all data
        products_info = "\n".join([
            f"- {p.get('title', 'N/A')} | Price: {p.get('price', 'N/A')} | Rating: {p.get('rating', 'N/A')} | Platform: {p.get('platform', 'N/A')}"
            for p in state.get("products_found", [])[:5]
        ]) or "No products found"
        
        history_info = "\n".join([
            f"- {h.get('title', 'N/A')}: {h.get('snippet', 'N/A')[:150]}"
            for h in state.get("price_history", [])[:3]
        ]) or "No price history available"
        
        market_info = "\n".join([
            f"- {s.get('title', 'N/A')}: {s.get('snippet', 'N/A')[:150]}"
            for s in state.get("upcoming_sales", [])[:3]
        ]) or "No upcoming sales data"
        
        deals_info = "\n".join([
            f"- {d.get('title', 'N/A')}: {d.get('snippet', 'N/A')[:150]}"
            for d in state.get("product_deals", [])[:3]
        ]) or "No deals found"
        
        try:
            response = llm.invoke([
                SystemMessage(content="""You are an expert AI shopping analyst for Indian consumers in 2026.
You analyze product prices and give clear, actionable recommendations.
Always mention prices in INR and be transparent about data availability.
Today's year is 2026."""),
                
                HumanMessage(content=f"""Analyze this data for '{product_name}' and give recommendation:

CURRENT PRODUCTS:
{products_info}

PRICE HISTORY:
{history_info}

UPCOMING SALES:
{market_info}

PRODUCT DEALS:
{deals_info}

Give me:
1. CURRENT PRICE
2. HISTORICAL LOW
3. BUY OR WAIT
4. BEST TIME TO BUY
5. RECOMMENDATION (2 sentences)

Format clearly with these headings.""")
            ])
            
            prediction = response.content
            app_logger.info("Agent 4 complete")
            
            return {"ai_prediction": prediction}
            
        except Exception as e:
            app_logger.warning(f"LLM call failed: {str(e)}, returning generic recommendation")
            generic_rec = f"Based on current market data for {product_name}:\n1. Check actual prices on Amazon.in\n2. Consider waiting for upcoming sales\n3. Compare with alternatives\nRecommendation: Monitor prices for next 2 weeks before deciding."
            return {"ai_prediction": generic_rec}
        
    except Exception as e:
        app_logger.error(f"Agent 4 error: {str(e)}", exc_info=True)
        return {
            "ai_prediction": "Unable to generate recommendation due to technical error",
            "error": str(e)
        }