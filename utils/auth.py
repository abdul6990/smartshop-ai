import os
import random
import string
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

_OTP_MEMORY_STORE: dict[str, dict[str, str]] = {}

def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


def _store_otp_in_memory(email: str, otp: str, expires_at: str) -> None:
    _OTP_MEMORY_STORE[email.lower()] = {
        "otp": otp,
        "otp_expires_at": expires_at,
    }


def _load_otp_from_memory(email: str) -> dict | None:
    return _OTP_MEMORY_STORE.get(email.lower())


def _clear_otp_from_memory(email: str) -> None:
    _OTP_MEMORY_STORE.pop(email.lower(), None)


def _parse_verification_token(token: str) -> tuple[str | None, str | None]:
    if not token or "|" not in token:
        return None, None
    otp_code, expires_at = token.split("|", 1)
    otp_code = otp_code.strip()
    expires_at = expires_at.strip()
    if not otp_code or not expires_at:
        return None, None
    return otp_code, expires_at


def _parse_iso_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def _ensure_user_exists(db, email: str) -> dict:
    existing = db.table("users").select("id,email").eq("email", email).execute()
    if existing.data:
        return existing.data[0]

    placeholder_hash = hashlib.sha256(f"otp:{email}".encode()).hexdigest()
    insert_attempts = [
        {
            "email": email,
            "password_hash": placeholder_hash,
            "is_verified": False,
            "verification_token": None,
        },
        {
            "email": email,
            "password_hash": placeholder_hash,
        },
        {
            "email": email,
        },
    ]

    last_error = None
    for payload in insert_attempts:
        try:
            created = db.table("users").insert(payload).execute()
            if created.data:
                return created.data[0]
        except Exception as exc:
            last_error = exc

    lookup = db.table("users").select("id,email").eq("email", email).execute()
    if lookup.data:
        return lookup.data[0]

    if last_error:
        raise last_error
    raise Exception("Failed to create or fetch user for OTP flow")


def _store_otp_record(db, email: str, otp: str, expires_at: str) -> str:
    # Always keep a process-local backup so OTP verify can still work when
    # schema is partially migrated.
    _store_otp_in_memory(email, otp, expires_at)

    try:
        db.table("otp_verifications").upsert(
            {
                "email": email,
                "otp": otp,
                "otp_expires_at": expires_at,
            },
            on_conflict="email",
        ).execute()
        return "otp_verifications"
    except Exception:
        pass

    try:
        _ensure_user_exists(db, email)
        token_value = f"{otp}|{expires_at}"
        try:
            db.table("users").update(
                {
                    "verification_token": token_value,
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("email", email).execute()
        except Exception:
            db.table("users").update(
                {
                    "verification_token": token_value,
                }
            ).eq("email", email).execute()
        return "users.verification_token"
    except Exception:
        return "memory"


def _load_otp_record(db, email: str) -> dict | None:
    try:
        result = db.table("otp_verifications").select("otp,otp_expires_at").eq("email", email).limit(1).execute()
        if result.data:
            record = result.data[0]
            otp_value = record.get("otp")
            expires = record.get("otp_expires_at")
            if otp_value and expires:
                return {
                    "otp": otp_value,
                    "otp_expires_at": expires,
                    "source": "otp_verifications",
                }
    except Exception:
        pass

    try:
        result = db.table("users").select("verification_token").eq("email", email).limit(1).execute()
        if result.data:
            token = result.data[0].get("verification_token")
            otp_value, expires = _parse_verification_token(token)
            if otp_value and expires:
                return {
                    "otp": otp_value,
                    "otp_expires_at": expires,
                    "source": "users.verification_token",
                }
    except Exception:
        pass

    memory_record = _load_otp_from_memory(email)
    if memory_record:
        return {
            "otp": memory_record["otp"],
            "otp_expires_at": memory_record["otp_expires_at"],
            "source": "memory",
        }
    return None


def _clear_otp_record(db, email: str, source: str) -> None:
    _clear_otp_from_memory(email)
    if source == "otp_verifications":
        try:
            db.table("otp_verifications").delete().eq("email", email).execute()
        except Exception:
            pass
    elif source == "users.verification_token":
        try:
            db.table("users").update(
                {
                    "verification_token": None,
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("email", email).execute()
        except Exception:
            try:
                db.table("users").update(
                    {
                        "verification_token": None,
                    }
                ).eq("email", email).execute()
            except Exception:
                pass

def send_otp_email(email: str, otp: str) -> tuple[bool, str]:
    try:
        from utils.logger import app_logger
        import json
        import smtplib
        import urllib.request
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Preferred: transactional email provider over HTTPS (works better on Render).
        # If RESEND_API_KEY is set, send the OTP using Resend.
        resend_api_key = os.getenv("RESEND_API_KEY")
        resend_from = os.getenv("RESEND_FROM_EMAIL") or os.getenv("EMAIL_ADDRESS")
        if resend_api_key and resend_from:
            payload = json.dumps({
                "from": resend_from,
                "to": [email],
                "subject": "SmartShop AI - Your OTP Code",
                "html": f"""
                <html><body style="font-family: Arial; background: #0A0A0F; color: white; padding: 20px;">
                <h2 style="color: #7C3AED;">SmartShop AI 🛒</h2>
                <p>Your verification code is:</p>
                <h1 style="color: #06B6D4; font-size: 48px; letter-spacing: 10px;">{otp}</h1>
                <p style="color: #94A3B8;">This code expires in 10 minutes.</p>
                </body></html>
                """,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=payload,
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json",
                    # Resend rejects direct HTTP requests without this header.
                    "User-Agent": "smartshop-ai/1.0",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    if 200 <= response.status < 300:
                        return True, "OTP sent successfully"
                    return False, f"Resend API returned HTTP {response.status}"
            except Exception as exc:
                app_logger.warning("Resend email send failed for %s: %s", email, str(exc))
                # Do not fall back to SMTP: Render free services block SMTP
                # ports and that obscures the useful Resend error.
                return False, f"Resend email delivery failed: {str(exc)}"

        sender_email = os.getenv("EMAIL_ADDRESS")
        sender_password = os.getenv("EMAIL_PASSWORD")
        
        if not sender_email or sender_email.startswith('your_'):
            return False, "Email not configured - set EMAIL_ADDRESS in .env"
        if not sender_password or sender_password.startswith('your_'):
            return False, "Email password not configured - set EMAIL_PASSWORD in .env"

        msg = MIMEMultipart()
        msg['From'] = sender_email
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
        attempts = [
            ("smtp.gmail.com", 587, "starttls"),
            ("smtp.gmail.com", 465, "ssl"),
        ]

        last_error = None
        for host, port, mode in attempts:
            try:
                if mode == "ssl":
                    with smtplib.SMTP_SSL(host, port, timeout=20) as server:
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, email, msg.as_string())
                else:
                    with smtplib.SMTP(host, port, timeout=20) as server:
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, email, msg.as_string())
                return True, "OTP sent successfully"
            except Exception as exc:
                last_error = exc
                app_logger.warning("OTP send attempt failed via %s:%s (%s): %s", host, port, mode, str(exc))

        if last_error:
            raise last_error
        return False, "Email delivery failed"
    except Exception as e:
        from utils.logger import app_logger
        error_msg = f"Email error: {str(e)}"
        app_logger.error(error_msg)
        return False, error_msg

def request_otp(email: str) -> dict:
    try:
        from utils.logger import app_logger
        db = get_supabase()
        otp = generate_otp()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

        otp_store_source = _store_otp_record(db, email, otp, expires_at)

        sent, message = send_otp_email(email, otp)
        if sent:
            app_logger.info(f"OTP successfully sent to {email} (stored via {otp_store_source})")
            return {"success": True, "message": "OTP sent to your email!"}
        else:
            app_logger.warning(f"OTP email failed for {email}: {message}")
            return {"success": False, "error": message}
    except Exception as e:
        from utils.logger import app_logger
        app_logger.error(f"OTP request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def verify_otp(email: str, otp: str) -> dict:
    try:
        from utils.logger import app_logger
        db = get_supabase()

        record = _load_otp_record(db, email)
        if not record:
            return {"success": False, "error": "OTP not found. Request a new one"}

        if record["otp"] != otp:
            return {"success": False, "error": "Invalid OTP"}

        expires_at = _parse_iso_datetime(record["otp_expires_at"])
        now = datetime.now(expires_at.tzinfo) if expires_at.tzinfo else datetime.now()
        if now > expires_at:
            return {"success": False, "error": "OTP expired. Request a new one"}

        _clear_otp_record(db, email, record["source"])

        try:
            user = _ensure_user_exists(db, email)
        except Exception as user_exc:
            app_logger.warning(
                "OTP verified but user upsert failed for %s: %s",
                email,
                str(user_exc),
            )
            user = {
                "id": email,
                "email": email,
            }

        # ✅ Create default wishlist if doesn't exist
        user_id = user.get("id", email)
        try:
            wishlist_check = db.table('wishlists')\
                .select('id')\
                .eq('user_id', user_id)\
                .eq('is_default', True)\
                .execute()
            
            if not wishlist_check.data:
                db.table('wishlists').insert({
                    'user_id': user_id,
                    'name': 'My Wishlist',
                    'is_default': True,
                    'is_public': False
                }).execute()
                app_logger.info(f"✅ Default wishlist created for {email}")
        except Exception as wl_exc:
            app_logger.warning(f"Failed to create default wishlist: {wl_exc}")

        return {
            "success": True,
            "user_id": user_id,
            "email": user.get("email", email)
        }
    except Exception as e:
        from utils.logger import app_logger
        app_logger.error(f"OTP verify failed: {str(e)}")
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
