from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, SystemMessage
import os

def run_ai_predictor(state: dict) -> dict:
    """
    Agent 4: AI Predictor
    Analyzes ALL data from previous agents
    and gives buy/wait recommendation
    """
    llm = ChatCohere(
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        model="command-r-plus-08-2024"
    )

    product_name = state["product_name"]

    print(f"\n🤖 Agent 4: AI analyzing data for '{product_name}'...")

    # Compile all data from previous agents
    products_info = "\n".join([
    f"- {p['title']} | Price: {p.get('price','N/A')} | Rating: {p.get('rating','N/A')} | Reviews: {p.get('reviews','N/A')}"
    for p in state.get("products_found", [])
])

    history_info = "\n".join([
        f"- {h['title']}: {h['content'][:200]}"
        for h in state.get("price_history", [])
    ])

    market_info = "\n".join([
        f"- {s['title']}: {s['content'][:200]}"
        for s in state.get("upcoming_sales", [])
    ])

    deals_info = "\n".join([
        f"- {d['title']}: {d['content'][:200]}"
        for d in state.get("product_deals", [])
    ])

    alternatives_info = "\n".join([
    f"- {a['title']} | Price: {a.get('price','N/A')} | Rating: {a.get('rating','N/A')}"
    for a in state.get("alternatives_found", [])
])

    # Ask LLM to analyze everything
    response = llm.invoke([
        SystemMessage(content="""You are an expert AI shopping analyst for Indian consumers in 2026.
You analyze product prices from multiple sources and give clear recommendations.
When prices are inconsistent across sources:
- Always mention the RANGE (lowest to highest found)
- Recommend checking Amazon.in directly for real-time price
- Be transparent that prices vary by seller
Always mention prices in INR. Today's year is 2026."""),

        HumanMessage(content=f"""Analyze this data for '{product_name}' and give a complete recommendation:

CURRENT PRODUCT DATA:
{products_info}

PRICE HISTORY:
{history_info}

UPCOMING SALES & MARKET:
{market_info}

PRODUCT SPECIFIC DEALS:
{deals_info}

CHEAPER ALTERNATIVES:
{alternatives_info}

Give me:
1. CURRENT PRICE: What is the current price on Amazon India?
2. HISTORICAL LOW: What was the lowest price ever?
3. BUY OR WAIT: Should I buy now or wait? (be specific)
4. BEST TIME TO BUY: When exactly should I buy?
5. UPCOMING SALES: Any sales coming up I should wait for?
6. CHEAPER ALTERNATIVES: Better value options?
7. OVERALL RECOMMENDATION: Final advice in 2 sentences

Format your response clearly with these exact headings.""")
    ])

    prediction = response.content
    print(f"✅ Agent 4 done!")

    return {"ai_prediction": prediction}