import os
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email: str, otp: str) -> bool:
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = os.getenv("EMAIL_ADDRESS")
        msg['To'] = email
        msg['Subject'] = "SmartShop AI - Your OTP Code"
        body = f"""
        <html><body style="font-family: Arial; background: #0A0A0F; color: white; padding: 20px;">
        <h2 style="color: #7C3AED;">SmartShop AI 🛒</h2>
        <p>Your verification code is:</p>
        <h1 style="color: #06B6D4; font-size: 48px; letter-spacing: 10px;">{otp}</h1>
        <p style="color: #94A3B8;">This code expires in 10 minutes.</p>
        </body></html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
        server.sendmail(os.getenv("EMAIL_ADDRESS"), email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def request_otp(email: str) -> dict:
    try:
        db = get_supabase()
        otp = generate_otp()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

        existing = db.table("users").select("*").eq("email", email).execute()
        if existing.data:
            db.table("users").update({
                "otp": otp,
                "otp_expires_at": expires_at
            }).eq("email", email).execute()
        else:
            db.table("users").insert({
                "email": email,
                "otp": otp,
                "otp_expires_at": expires_at
            }).execute()

        sent = send_otp_email(email, otp)
        if sent:
            return {"success": True, "message": "OTP sent to your email!"}
        else:
            return {"success": False, "error": "Failed to send OTP email"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_otp(email: str, otp: str) -> dict:
    try:
        db = get_supabase()
        result = db.table("users").select("*").eq("email", email).execute()

        if not result.data:
            return {"success": False, "error": "User not found"}

        user = result.data[0]

        if user["otp"] != otp:
            return {"success": False, "error": "Invalid OTP"}

        expires_at = datetime.fromisoformat(user["otp_expires_at"])
        if datetime.now() > expires_at:
            return {"success": False, "error": "OTP expired. Request a new one"}

        db.table("users").update({
            "otp": None,
            "otp_expires_at": None
        }).eq("email", email).execute()

        return {
            "success": True,
            "user_id": user["id"],
            "email": user["email"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def save_tracked_product(user_id: str, product_name: str, price: str, url: str, platform: str = "Amazon") -> bool:
    try:
        db = get_supabase()
        db.table("tracked_products").insert({
            "user_id": user_id,
            "product_name": product_name,
            "last_price": price,
            "product_url": url,
            "platform": platform,
            "alert_sent": False
        }).execute()
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def get_user_tracked_products(user_id: str) -> list:
    try:
        db = get_supabase()
        result = db.table("tracked_products").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"Fetch error: {e}")
        return []