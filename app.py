import streamlit as st
from dotenv import load_dotenv
import json
import os
from datetime import datetime
from graph.pipeline import run_price_pipeline

load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────
st.set_page_config(
    page_title="AI Price Intelligence",
    page_icon="🛒",
    layout="wide"
)

# ── CUSTOM CSS (makes it look professional) ───────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF9900, #FF6600);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FF9900;
        margin: 10px 0;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .status-tracking { color: #FF9900; font-weight: bold; }
    .status-dropped { color: #28a745; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛒 AI Price Intelligence Agent</h1>
    <p>Track Amazon prices • AI predictions • Real-time alerts</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=150)
    st.markdown("### 🤖 How It Works")
    st.markdown("""
    1. 🔍 **Agent 1** finds product on Amazon
    2. 📊 **Agent 2** checks price history
    3. 📰 **Agent 3** analyzes market & sales
    4. 🤖 **Agent 4** predicts best buy time
    5. 🔔 **Agent 5** sets up email alert
    """)
    st.divider()
    st.markdown("### 📊 Stats")
    
    # Load tracked products
    tracked = []
    if os.path.exists("data/tracked_products.json"):
        with open("data/tracked_products.json", "r") as f:
            content = f.read().strip()
            tracked = json.loads(content) if content else []
    
    st.metric("Products Tracked", len(tracked))
    st.metric("Alerts Active", len([t for t in tracked if not t.get("alert_triggered")]))

# ── MAIN TABS ─────────────────────────────────────
tab1, tab2 = st.tabs(["🔍 Track New Product", "📊 My Tracker"])

# ════════════════════════════════════════════════
# TAB 1: TRACK NEW PRODUCT
# ════════════════════════════════════════════════
with tab1:
    st.subheader("🔍 Analyze a Product")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input(
            "Product Name",
            placeholder="e.g. Samsung Galaxy S24, iPhone 15, Sony WH-1000XM5"
        )
    
    with col2:
        user_email = st.text_input(
            "Your Email (for alerts)",
            placeholder="yourname@gmail.com"
        )
    
    analyze_btn = st.button("🚀 Analyze with AI", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not product_name or not user_email:
            st.error("⚠️ Please fill in both fields!")
        else:
            # Progress tracking
            st.divider()
            st.markdown("### 🤖 Agents Working...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            agent_status = st.container()
            with agent_status:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    a1 = st.empty()
                    a1.markdown("🔍 **Finder**\n⏳ Waiting")
                with col2:
                    a2 = st.empty()
                    a2.markdown("📊 **Historian**\n⏳ Waiting")
                with col3:
                    a3 = st.empty()
                    a3.markdown("📰 **Analyzer**\n⏳ Waiting")
                with col4:
                    a4 = st.empty()
                    a4.markdown("🤖 **Predictor**\n⏳ Waiting")
                with col5:
                    a5 = st.empty()
                    a5.markdown("🔔 **Alert**\n⏳ Waiting")
            
            try:
                # Update progress as agents run
                status_text.info("🔍 Agent 1: Searching Amazon...")
                a1.markdown("🔍 **Finder**\n🔄 Running")
                progress_bar.progress(20)
                
                # Run the full pipeline
                result = run_price_pipeline(product_name, user_email)
                
                # Update all agents to done
                a1.markdown("🔍 **Finder**\n✅ Done")
                progress_bar.progress(40)
                a2.markdown("📊 **Historian**\n✅ Done")
                progress_bar.progress(60)
                a3.markdown("📰 **Analyzer**\n✅ Done")
                progress_bar.progress(80)
                a4.markdown("🤖 **Predictor**\n✅ Done")
                progress_bar.progress(90)
                a5.markdown("🔔 **Alert**\n✅ Done")
                progress_bar.progress(100)
                
                status_text.success("✅ All 5 agents completed!")
                
                st.divider()
                
                # ── RESULTS ──
                st.markdown("### 📊 AI Analysis Results")
                
                # Prediction in a nice box
                st.markdown("#### 🤖 AI Recommendation")
                st.markdown(
                    f'<div class="agent-card">{result["ai_prediction"]}</div>',
                    unsafe_allow_html=True
                )
                
                st.divider()
                
                # Show raw research in expander
                with st.expander("🔍 View Raw Research Data"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Products Found:**")
                        for p in result.get("products_found", []):
                            st.markdown(f"• [{p['title'][:60]}...]({p['url']})")
                    with col2:
                        st.markdown("**Alternatives Found:**")
                        for a in result.get("alternatives_found", []):
                            st.markdown(f"• [{a['title'][:60]}...]({a['url']})")
                
                # Alert confirmation
                st.success(f"🔔 {result['alert_status']}")
                st.info(f"📧 Check your email at **{user_email}** for the full AI report!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Check your API keys in the .env file")

# ════════════════════════════════════════════════
# TAB 2: APPLICATION TRACKER
# ════════════════════════════════════════════════
with tab2:
    st.subheader("📊 Your Tracked Products")
    
    # Reload tracked products
    tracked = []
    if os.path.exists("data/tracked_products.json"):
        with open("data/tracked_products.json", "r") as f:
            content = f.read().strip()
            tracked = json.loads(content) if content else []
    
    if not tracked:
        st.info("👆 No products tracked yet! Go to 'Track New Product' tab to get started.")
    else:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tracked", len(tracked))
        with col2:
            st.metric("Active Alerts", len([t for t in tracked if not t.get("alert_triggered")]))
        with col3:
            st.metric("Alerts Triggered", len([t for t in tracked if t.get("alert_triggered")]))
        
        st.divider()
        
        # Show each tracked product
        for i, product in enumerate(reversed(tracked)):
            with st.expander(
                f"🛒 {product['product_name']} — Added {product['date_added']}",
                expanded=(i == 0)
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**🤖 AI Prediction:**")
                    st.markdown(product.get("prediction", "No prediction available"))
                
                with col2:
                    st.markdown("**📋 Details:**")
                    st.markdown(f"📧 **Email:** {product['user_email']}")
                    st.markdown(f"📅 **Added:** {product['date_added']}")
                    
                    status = product.get("status", "Tracking")
                    if status == "Tracking":
                        st.markdown(f"🟡 **Status:** {status}")
                    else:
                        st.markdown(f"🟢 **Status:** {status}")
                    
                    # Manual status update
                    new_status = st.selectbox(
                        "Update Status",
                        ["Tracking", "Price Dropped", "Purchased", "Cancelled"],
                        key=f"status_{i}"
                    )
                    
                    if st.button("Update", key=f"update_{i}"):
                        tracked[-(i+1)]["status"] = new_status
                        with open("data/tracked_products.json", "w") as f:
                            json.dump(tracked, f, indent=2)
                        st.success("✅ Status updated!")
                        st.rerun()

# ── FOOTER ────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🤖 **Powered by:** LangGraph + Cohere")
with col2:
    st.markdown("🔍 **Data from:** Tavily Search")
with col3:
    st.markdown("📧 **Alerts via:** Gmail SMTP")