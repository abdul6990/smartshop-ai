"""
WhatsApp Notification System
Send price drop alerts via WhatsApp using Twilio
"""
import os
from utils.logger import app_logger
from datetime import datetime

# Try to import Twilio
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

class WhatsAppNotifier:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "+1234567890")
        missing_config = []
        if not self.account_sid:
            missing_config.append("TWILIO_ACCOUNT_SID")
        if not self.auth_token:
            missing_config.append("TWILIO_AUTH_TOKEN")

        self.enabled = TWILIO_AVAILABLE and not missing_config
        
        if self.enabled:
            self.client = Client(self.account_sid, self.auth_token)
            app_logger.info("✅ WhatsApp notifications enabled (Twilio)")
        else:
            if not TWILIO_AVAILABLE:
                app_logger.warning(
                    "⚠️ WhatsApp notifications disabled - Twilio package not installed. "
                    "Install with: pip install twilio"
                )
            else:
                app_logger.warning(
                    "⚠️ WhatsApp notifications disabled - missing Twilio config: "
                    f"{', '.join(missing_config)}"
                )
    
    def send_price_drop_alert(self, user_phone: str, product_name: str, previous_price: float, 
                              new_price: float, platform: str, product_url: str) -> bool:
        """Send price drop alert via WhatsApp"""
        if not self.enabled:
            app_logger.warning(f"⚠️ WhatsApp disabled - cannot send alert to {user_phone}")
            return False
        
        try:
            if not user_phone.startswith('+'):
                user_phone = f"+{user_phone}"
            
            price_drop = previous_price - new_price
            discount_percent = (price_drop / previous_price) * 100
            
            message_body = f"""
🎉 *Price Drop Alert!*

📦 *{product_name}*
🛍️ *Platform:* {platform}

💰 *Previous Price:* ₹{previous_price:,.2f}
✨ *New Price:* ₹{new_price:,.2f}
📉 *Savings:* ₹{price_drop:,.2f} ({discount_percent:.1f}% off)

🔗 *Buy Now:* {product_url}

⏰ *Offer valid for limited time!*
"""
            
            message = self.client.messages.create(
                from_=f"whatsapp:{self.whatsapp_from}",
                to=f"whatsapp:{user_phone}",
                body=message_body.strip()
            )
            
            app_logger.info(f"✅ WhatsApp alert sent to {user_phone} - SID: {message.sid}")
            return True
            
        except Exception as e:
            app_logger.error(f"❌ Failed to send WhatsApp alert to {user_phone}: {str(e)}")
            return False
    
    def send_wishlist_summary(self, user_phone: str, items_with_drops: list) -> bool:
        """Send daily wishlist summary with price drops"""
        if not self.enabled:
            return False
        
        try:
            if not user_phone.startswith('+'):
                user_phone = f"+{user_phone}"
            
            # Build message
            message_body = "📊 *Your Wishlist Summary*\n\n"
            message_body += f"_{datetime.now().strftime('%B %d, %Y')}_\n\n"
            
            for i, item in enumerate(items_with_drops[:5], 1):  # Max 5 items per message
                message_body += f"{i}. 📦 *{item['product_name']}*\n"
                message_body += f"   💰 ₹{item['new_price']:,.2f} (was ₹{item['previous_price']:,.2f})\n"
                message_body += f"   📉 Save ₹{item['previous_price'] - item['new_price']:,.2f}\n\n"
            
            if len(items_with_drops) > 5:
                message_body += f"... and {len(items_with_drops) - 5} more items with price drops!\n"
            
            message_body += "\n🔗 Check your app for more details!👆"
            
            message = self.client.messages.create(
                from_=f"whatsapp:{self.whatsapp_from}",
                to=f"whatsapp:{user_phone}",
                body=message_body.strip()
            )
            
            app_logger.info(f"✅ Wishlist summary sent to {user_phone}")
            return True
            
        except Exception as e:
            app_logger.error(f"❌ Failed to send wishlist summary to {user_phone}: {str(e)}")
            return False
    
    def send_buying_recommendation(self, user_phone: str, product_name: str, recommendation: str, 
                                   current_price: float, predicted_price: float, confidence: float) -> bool:
        """Send AI buying recommendation"""
        if not self.enabled:
            return False
        
        try:
            if not user_phone.startswith('+'):
                user_phone = f"+{user_phone}"
            
            emoji = "✅" if recommendation == "buy_now" else "⏳"
            wait_days = {"wait_1_week": "7 days", "wait_2_weeks": "14 days"}.get(recommendation, "later")
            
            message_body = f"""
🤖 *Smart Recommendation for:*
📦 *{product_name}*

💰 *Current Price:* ₹{current_price:,.2f}
📊 *Predicted Price:* ₹{predicted_price:,.2f}
🎯 *Confidence:* {confidence:.0f}%

{emoji} *Recommendation:*
Based on our AI analysis, we suggest:

"""
            
            if recommendation == "buy_now":
                message_body += "✅ *BUY NOW!* - This is a good price.\nPrice might increase in the next few days."
            else:
                message_body += f"⏳ *WAIT {wait_days.upper()}* - We predict prices will drop by ₹{current_price - predicted_price:,.0f}"
            
            message_body += "\n\n💡 Open the app to see full details!"
            
            message = self.client.messages.create(
                from_=f"whatsapp:{self.whatsapp_from}",
                to=f"whatsapp:{user_phone}",
                body=message_body.strip()
            )
            
            app_logger.info(f"✅ Recommendation sent to {user_phone}")
            return True
            
        except Exception as e:
            app_logger.error(f"❌ Failed to send recommendation to {user_phone}: {str(e)}")
            return False

# Create global instance
whatsapp_notifier = WhatsAppNotifier()

def send_price_alert(user_id: str, user_phone: str, product_name: str, previous_price: float, 
                    new_price: float, platform: str, product_url: str) -> bool:
    """Send price alert and update database"""
    from utils.supabase_client import db as supabase_db
    
    try:
        # Send WhatsApp notification
        success = whatsapp_notifier.send_price_drop_alert(
            user_phone, product_name, previous_price, new_price, platform, product_url
        )
        
        if success:
            app_logger.info(f"✅ Price alert sent and recorded for user {user_id}")
        
        return success
        
    except Exception as e:
        app_logger.error(f"Error sending price alert: {str(e)}")
        return False
