"""Input validation utilities for API requests"""
import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or len(email) > 254:
        return False, "Email is required and must be less than 254 characters"
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""

def validate_product_name(product_name: str, max_length: int = 200) -> Tuple[bool, str]:
    """Validate product name input"""
    product_name = product_name.strip()
    if not product_name:
        return False, "Product name is required"
    if len(product_name) > max_length:
        return False, f"Product name must be less than {max_length} characters"
    if len(product_name) < 2:
        return False, "Product name must be at least 2 characters"
    # Allow alphanumeric, spaces, hyphens, commas, brackets, slashes, plus, and other common product name chars
    if not re.match(r"^[a-zA-Z0-9\s\-,&.()\/\[\]\+°™®]+$", product_name):
        return False, "Product name contains invalid characters"
    return True, ""

def validate_otp(otp: str) -> Tuple[bool, str]:
    """Validate OTP format (6 digits)"""
    otp = otp.strip()
    if not otp or not re.match(r"^\d{6}$", otp):
        return False, "OTP must be exactly 6 digits"
    return True, ""

def validate_user_id(user_id: str) -> Tuple[bool, str]:
    """Validate user ID format"""
    user_id = user_id.strip()
    if not user_id:
        return False, "User ID is required"
    if len(user_id) < 5 or len(user_id) > 50:
        return False, "Invalid user ID format"
    return True, ""

def validate_price(price: str) -> Tuple[bool, str]:
    """Validate price format"""
    price = price.strip()
    # Allow currency symbols and numbers
    if not re.match(r"^[₹$€£]?\s*[\d,]+(?:\.\d{1,2})?$", price):
        return False, "Invalid price format"
    return True, ""
