import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_price_alert(to_email: str, product_name: str, prediction: str):
    """
    Sends a price drop alert email
    Uses Gmail SMTP (free)
    """
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🛒 Price Alert: {product_name} - AI Recommendation Ready!"
    msg["From"] = from_email
    msg["To"] = to_email

    # Email body
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #FF9900;">🛒 AI Price Intelligence Alert</h2>
        <h3>Product: {product_name}</h3>
        <hr>
        <h4>🤖 AI Recommendation:</h4>
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">
            <pre style="white-space: pre-wrap;">{prediction}</pre>
        </div>
        <hr>
        <p style="color: #666; font-size: 12px;">
            Powered by AI Price Intelligence Agent
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False