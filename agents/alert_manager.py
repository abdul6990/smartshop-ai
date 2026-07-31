"""
Agent 5: Alert Manager
Saves tracked products and manages alerts
"""
import json
import os
from datetime import datetime
from utils.logger import app_logger

def run_alert_manager(state: dict) -> dict:
    """
    Agent 5: Alert Manager
    Saves product to tracking list
    """
    try:
        product_name = state.get("product_name", "").strip()
        user_email = state.get("user_email", "").strip()
        prediction = state.get("ai_prediction", "")
        
        if not product_name or not user_email:
            app_logger.error("Agent 5: Missing product name or email")
            return {
                "alert_status": "❌ Failed: Missing required information",
                "error": "Product name and email required"
            }
        
        app_logger.info(f"Agent 5: Saving '{product_name}' for {user_email}")
        
        tracked_file = "data/tracked_products.json"
        
        # Read existing products
        tracked = []
        if os.path.exists(tracked_file):
            try:
                with open(tracked_file, "r") as f:
                    content = f.read().strip()
                    tracked = json.loads(content) if content else []
            except Exception as e:
                app_logger.warning(f"Failed to read tracked products file: {str(e)}")
                tracked = []
        
        # Create new entry
        new_entry = {
            "id": len(tracked) + 1,
            "product_name": product_name,
            "user_email": user_email,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prediction": prediction[:500],  # Limit size
            "status": "Tracking",
            "alert_triggered": False,
            "platform": state.get("best_product", {}).get("platform", "Unknown"),
            "current_price": state.get("best_product", {}).get("price", "N/A")
        }
        
        # Save
        try:
            tracked.append(new_entry)
            with open(tracked_file, "w") as f:
                json.dump(tracked, f, indent=2)
            app_logger.info(f"Product saved successfully. ID: {new_entry['id']}")
        except Exception as e:
            app_logger.error(f"Failed to save tracked product: {str(e)}")
            return {
                "alert_status": f"❌ Failed to save: {str(e)}",
                "error": str(e)
            }
        
        return {
            "alert_status": f"✅ '{product_name}' is now being tracked! (ID: {new_entry['id']})"
        }
        
    except Exception as e:
        app_logger.error(f"Agent 5 error: {str(e)}", exc_info=True)
        return {
            "alert_status": f"❌ Error: {str(e)}",
            "error": str(e)
        }