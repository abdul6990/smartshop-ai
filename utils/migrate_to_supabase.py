#!/usr/bin/env python3
"""
Migration Script: JSON Data to Supabase
Safely migrates existing tracked products from JSON to Supabase
"""
import json
import os
from datetime import datetime
from pathlib import Path

def migrate_tracked_products():
    """Migrate tracked_products.json to Supabase"""
    try:
        from utils.supabase_client import db
        
        json_file = Path("data/tracked_products.json")
        
        if not json_file.exists():
            print("❌ No tracked_products.json found")
            return False
        
        with open(json_file, 'r') as f:
            products = json.load(f)
        
        print(f"📦 Migrating {len(products)} products...")
        
        for product in products:
            # Extract user_id from product or use default
            user_id = product.get("user_id", "default_user")
            
            # Prepare product data
            product_data = {
                "title": product.get("title"),
                "price": product.get("price"),
                "platform": product.get("platform"),
                "url": product.get("url"),
                "status": product.get("status", "Tracking"),
                "rating": product.get("rating"),
                "reviews": product.get("reviews")
            }
            
            # Add to Supabase
            success = db.add_tracked_product(user_id, product_data)
            
            if success:
                print(f"✅ Migrated: {product_data['title'][:50]}")
            else:
                print(f"⚠️ Failed to migrate: {product_data['title'][:50]}")
        
        # Backup original JSON
        backup_file = f"data/tracked_products.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import shutil
        shutil.copy(json_file, backup_file)
        print(f"💾 Backup saved to: {backup_file}")
        
        return True
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def migrate_wishlist():
    """Migrate wishlist.json to Supabase (if exists)"""
    try:
        from utils.supabase_client import db
        
        json_file = Path("data/wishlist.json")
        
        if not json_file.exists():
            print("ℹ️ No wishlist.json found - skipping")
            return True
        
        with open(json_file, 'r') as f:
            wishlist_items = json.load(f)
        
        print(f"📦 Migrating {len(wishlist_items)} wishlist items...")
        
        for item in wishlist_items:
            user_id = item.get("user_id", "default_user")
            product = {
                "title": item.get("product_name"),
                "price": item.get("price"),
                "platform": item.get("platform"),
                "url": item.get("url"),
                "rating": item.get("rating")
            }
            
            db.add_to_wishlist(user_id, product)
            print(f"✅ Migrated wishlist: {product['title'][:50]}")
        
        # Backup
        backup_file = f"data/wishlist.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import shutil
        shutil.copy(json_file, backup_file)
        print(f"💾 Backup saved to: {backup_file}")
        
        return True
    
    except Exception as e:
        print(f"⚠️ Wishlist migration warning: {e}")
        return True


def main():
    """Run all migrations"""
    print("🚀 Starting Supabase Migration...")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Supabase credentials not found in .env")
        print("Please set SUPABASE_URL and SUPABASE_KEY")
        return False
    
    print("✅ Supabase credentials found\n")
    
    # Run migrations
    print("1️⃣ Migrating tracked products...")
    result1 = migrate_tracked_products()
    print()
    
    print("2️⃣ Migrating wishlist...")
    result2 = migrate_wishlist()
    print()
    
    if result1 and result2:
        print("=" * 50)
        print("✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Verify data in Supabase dashboard")
        print("   2. Test /tracked endpoint to confirm")
        print("   3. Consider archiving old JSON files")
        return True
    else:
        print("=" * 50)
        print("⚠️ Migration completed with warnings")
        return False


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    
    success = main()
    sys.exit(0 if success else 1)
