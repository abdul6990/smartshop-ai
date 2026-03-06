import json
import os
from datetime import datetime

def run_alert_manager(state: dict) -> dict:
    """
    Agent 5: Alert Manager
    Saves product to tracking list
    and sets up price drop alert
    """
    print(f"\n🔔 Agent 5: Setting up price alert...")

    product_name = state["product_name"]
    user_email = state.get("user_email", "")
    prediction = state.get("ai_prediction", "")

    # Save to tracked products JSON
    tracked_file = "data/tracked_products.json"

    # Load existing tracked products
    if os.path.exists(tracked_file):
        with open(tracked_file, "r") as f:
            content = f.read().strip()
            tracked = json.loads(content) if content else []
    else:
        tracked = []

    # Add new product
    new_entry = {
        "id": len(tracked) + 1,
        "product_name": product_name,
        "user_email": user_email,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prediction": prediction,
        "status": "Tracking",
        "alert_triggered": False
    }

    tracked.append(new_entry)

    # Save back to file
    with open(tracked_file, "w") as f:
        json.dump(tracked, f, indent=2)

    print(f"✅ Agent 5 done! Product saved to tracker")
    # Send email immediately with prediction
    if user_email and user_email != "test@gmail.com":
        from utils.email_sender import send_price_alert
        email_sent = send_price_alert(
            to_email=user_email,
            product_name=product_name,
            prediction=prediction
        )
        if email_sent:
            print(f"📧 Alert email sent to {user_email}!")
        else:
            print(f"⚠️ Email failed - check your Gmail credentials")

    return {
        "alert_status": f"✅ '{product_name}' is now being tracked! Alert will be sent to {user_email}"
    }