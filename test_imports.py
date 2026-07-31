#!/usr/bin/env python3
"""Test which import is causing the hang"""
import sys

print("✅ 1. Python started")
sys.stdout.flush()

from fastapi import FastAPI
print("✅ 2. FastAPI imported")
sys.stdout.flush()

from dotenv import load_dotenv
load_dotenv()
print("✅ 3. Dotenv loaded")
sys.stdout.flush()

from utils.logger import app_logger
print("✅ 4. Logger imported")
sys.stdout.flush()

from utils.cache import cache
print("✅ 5. Cache imported")
sys.stdout.flush()

from utils.price_charts import PriceChartManager
print("✅ 6. PriceChartManager imported")
sys.stdout.flush()

print("⚠️ About to import supabase_client...")
sys.stdout.flush()
from utils.supabase_client import db as supabase_db
print("✅ 7. Supabase client imported")
sys.stdout.flush()

print("⚠️ About to import product_service...")
sys.stdout.flush()
from utils.product_service import ProductCreate
print("✅ 8. ProductService imported")
sys.stdout.flush()

print("⚠️ About to import wishlist_service...")
sys.stdout.flush()
from utils.wishlist_service import WishlistResponse
print("✅ 9. WishlistService imported")
sys.stdout.flush()

print("✅ ALL IMPORTS SUCCESSFUL!")
