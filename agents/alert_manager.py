import json
import os
from datetime import datetime

def run_alert_manager(state: dict) -> dict:
    """
    Agent 5: Alert Manager
    Saves product to tracking list only
    (Email removed - WhatsApp alerts coming soon)
    """
    print(f"\n🔔 Agent 5: Saving to tracker...")

    product_name = state["product_name"]
    user_email = state.get("user_email", "")
    prediction = state.get("ai_prediction", "")
    best_product = state.get("best_product", {})

    tracked_file = "data/tracked_products.json"

    if os.path.exists(tracked_file):
        with open(tracked_file, "r") as f:
            content = f.read().strip()
            tracked = json.loads(content) if content else []
    else:
        tracked = []

    new_entry = {
        "id": len(tracked) + 1,
        "product_name": product_name,
        "user_email": user_email,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prediction": prediction,
        "status": "Tracking",
        "alert_triggered": False,
        "best_product": best_product
    }

    tracked.append(new_entry)

    with open(tracked_file, "w") as f:
        json.dump(tracked, f, indent=2)

    print(f"✅ Agent 5 done! Saved to tracker. No email sent.")

    return {
        "alert_status": f"✅ '{product_name}' is now being tracked!"
    }