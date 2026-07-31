import asyncio
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Load environment variables before any other imports that might use them
load_dotenv()

from utils.logger import app_logger
from utils.supabase_client import db as supabase_db
from agents.product_scraper import ProductScraper
from agents.price_tracker import PriceTracker
from utils.product_service import get_or_create_product

# Global scheduler instance
_scheduler: Optional[BackgroundScheduler] = None

class PriceScheduler:
    """
    Automated Price Monitoring Scheduler
    Runs background tasks to keep price data fresh and trigger alerts.
    """
    
    def __init__(self, interval_seconds: int = 3600):
        self.interval = interval_seconds
        self.is_running = False
        
    async def run_once(self):
        """Execute one cycle of price monitoring and notification dispatch"""
        app_logger.info("🚀 Starting automated monitoring & notification cycle...")
        start_time = time.time()
        
        try:
            # 1. Price Monitoring
            await self._monitor_prices()
            
            # 2. Notification Dispatching
            await self._dispatch_notifications()
                    
        except Exception as e:
            app_logger.error(f"Scheduler cycle error: {e}")
            
        elapsed = time.time() - start_time
        app_logger.info(f"🏁 Cycle completed in {elapsed:.2f}s")

    async def _monitor_prices(self):
        """Fetch wishlist items and update their latest prices"""
        try:
            # We need wishlist_item_id to link alerts properly
            items_res = supabase_db.table('wishlist_items').select('id, product_id, target_price').execute()
            if not items_res.data:
                return
                
            app_logger.info(f"Monitoring {len(items_res.data)} wishlist items...")
            
            async with ProductScraper() as scraper:
                for item in items_res.data:
                    await self._process_wishlist_item(item, scraper)
        except Exception as e:
            app_logger.error(f"Monitoring error: {e}")

    async def _process_wishlist_item(self, item: Dict, scraper: ProductScraper):
        """Process a single tracked item from a wishlist"""
        product_id = item['product_id']
        wishlist_item_id = item['id']
        target_price = item.get('target_price')
        
        try:
            # Get product name
            product_res = supabase_db.table('products').select('name').eq('id', product_id).execute()
            if not product_res.data:
                return
            
            product_name = product_res.data[0]['name']
            
            # Scrape latest prices (getting top result per platform)
            results = []
            results.extend(await scraper.search_amazon(product_name, max_results=1))
            results.extend(await scraper.search_flipkart(product_name, max_results=1))
            results.extend(await scraper.search_croma(product_name, max_results=1))
            
            for res in results:
                platform_name = res['platform']
                
                # Resolve Platform UUID
                platform_res = supabase_db.table('platforms').select('id').ilike('name', f"%{platform_name}%").limit(1).execute()
                if not platform_res.data:
                    continue
                p_id = platform_res.data[0]['id']
                
                price = res['price']
                url = res.get('url', 'https://smartshop-ai.com')
                
                # 1. Update/Insert into product_prices table (Schema: in_stock, product_url, scrape_source)
                supabase_db.table('product_prices').insert({
                    'product_id': product_id,
                    'platform_id': p_id,
                    'price': price,
                    'in_stock': True,
                    'product_url': url,
                    'scrape_source': platform_name.lower(),
                    'last_checked': datetime.now().isoformat()
                }).execute()
                
                # 2. Check for price drops and trigger alerts
                change = PriceTracker.track_price_change(product_id, p_id, price)
                if change and change.get('is_drop'):
                    # Check if it meets the user's specific target or significant drop
                    if not target_price or price <= target_price or change['change_percent'] > 10:
                        app_logger.info(f"🔔 Generating alert for {product_name} at ₹{price}")
                        
                        # We need the user_id associated with this wishlist item
                        user_res = supabase_db.table('wishlist_items')\
                            .select('wishlists(user_id)')\
                            .eq('id', wishlist_item_id).execute()
                            
                        user_id = user_res.data[0]['wishlists']['user_id'] if user_res.data else None
                        
                        if user_id:
                            supabase_db.table('price_alerts').insert({
                                'wishlist_item_id': wishlist_item_id,
                                'user_id': user_id,
                                'alert_type': 'price_drop',
                                'previous_price': change['previous_price'],
                                'new_price': change['new_price'],
                                'price_drop_amount': change['change_amount'],
                                'price_drop_percent': change['change_percent'],
                                'product_url': url,
                                'platform_id': p_id
                            }).execute()
                            
        except Exception as e:
            app_logger.error(f"Error processing item {wishlist_item_id}: {e}")

    async def _dispatch_notifications(self):
        """Check for unsent alerts and notify users"""
        try:
            # Get alerts where notification hasn't been sent yet
            unsent = supabase_db.table('price_alerts').select('*, wishlist_items(products(name))').eq('notification_sent', False).execute()
            
            if not unsent.data:
                return
                
            app_logger.info(f"📢 Dispatching {len(unsent.data)} pending notifications...")
            
            for alert in unsent.data:
                success = await self._send_alert_to_user(alert)
                if success:
                    # Mark as sent
                    supabase_db.table('price_alerts').update({'notification_sent': True}).eq('id', alert['id']).execute()
                    
        except Exception as e:
            app_logger.error(f"Notification dispatch error: {e}")

    async def _send_alert_to_user(self, alert: Dict) -> bool:
        """Send the actual notification via Email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            user_id = alert.get('user_id')
            product_name = alert.get('wishlist_items', {}).get('products', {}).get('name', 'Unknown')
            price = alert.get('new_price', 0)
            previous_price = alert.get('previous_price', 0)
            drop = alert.get('price_drop_percent', 0)
            product_url = alert.get('product_url', '')
            
            # Look up user email from database
            user_res = supabase_db.table('users').select('email').eq('id', user_id).limit(1).execute()
            if not user_res.data or not user_res.data[0].get('email'):
                app_logger.warning(f"No email found for user {user_id}, skipping notification")
                return True  # Mark as sent to avoid retry loops
            
            user_email = user_res.data[0]['email']
            
            # Send email via Gmail SMTP
            sender_email = os.getenv("EMAIL_ADDRESS")
            sender_password = os.getenv("EMAIL_PASSWORD")
            
            if not sender_email or not sender_password:
                app_logger.warning("Email not configured, logging alert instead")
                app_logger.info(f"📨 ALERT for {user_email}: {product_name} dropped to ₹{price:.2f} (-{drop:.1f}%)")
                return True
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = user_email
            msg['Subject'] = f"🔥 Price Drop Alert: {product_name} is now ₹{price:.0f}!"
            
            body = f"""
            <html><body style="font-family: Arial, sans-serif; background: #0A0A0F; color: white; padding: 30px;">
            <div style="max-width: 500px; margin: 0 auto; background: #161625; border-radius: 16px; padding: 30px; border: 1px solid rgba(255,255,255,0.08);">
                <h2 style="color: #7C3AED; margin-top: 0;">SmartShop AI 🛒</h2>
                <h3 style="color: #F8FAFC;">Price Drop Detected!</h3>
                <p style="color: #94A3B8;">Great news! A product you're tracking just got cheaper.</p>
                
                <div style="background: #0F0F1A; border-radius: 12px; padding: 20px; margin: 20px 0; border: 1px solid rgba(255,255,255,0.08);">
                    <p style="color: #F8FAFC; font-size: 18px; font-weight: bold; margin: 0 0 8px 0;">{product_name}</p>
                    <p style="color: #475569; margin: 0;">
                        <span style="text-decoration: line-through;">₹{previous_price:,.0f}</span>
                        <span style="color: #10B981; font-size: 24px; font-weight: bold; margin-left: 12px;">₹{price:,.0f}</span>
                    </p>
                    <p style="color: #10B981; margin: 8px 0 0 0;">📉 {drop:.1f}% price drop!</p>
                </div>
                
                {f'<a href="{product_url}" style="display: inline-block; background: linear-gradient(135deg, #7C3AED, #06B6D4); color: white; padding: 12px 24px; border-radius: 100px; text-decoration: none; font-weight: bold;">Grab This Deal →</a>' if product_url else ''}
                
                <p style="color: #475569; font-size: 12px; margin-top: 30px;">Sent by SmartShop AI Price Intelligence</p>
            </div>
            </body></html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
            server.quit()
            
            app_logger.info(f"📧 Email sent to {user_email}: {product_name} at ₹{price:.2f}")
            return True
            
        except Exception as e:
            app_logger.error(f"Failed to send alert email: {e}")
            return False

    async def start(self):
        """Start the continuous scheduler loop"""
        self.is_running = True
        app_logger.info(f"⏰ Scheduler started. Interval: {self.interval}s")
        
        while self.is_running:
            await self.run_once()
            app_logger.info(f"💤 Sleeping for {self.interval}s...")
            await asyncio.sleep(self.interval)

    def stop(self):
        """Stop the scheduler"""
        self.is_running = False


def start_background_scheduler():
    """
    Start the APScheduler background scheduler for price monitoring
    This is called from main.py on FastAPI startup
    """
    global _scheduler
    
    try:
        if _scheduler is not None and _scheduler.running:
            app_logger.warning("⚠️ Scheduler already running")
            return
        
        app_logger.info("🚀 Starting APScheduler for background jobs...")
        
        _scheduler = BackgroundScheduler()
        
        # Create a wrapper function to run the async scheduler as a sync job
        def run_price_monitoring():
            """Sync wrapper to run async price monitoring"""
            try:
                scheduler_instance = PriceScheduler(interval_seconds=21600)  # 6 hours
                asyncio.run(scheduler_instance.run_once())
            except Exception as e:
                app_logger.error(f"❌ Error in price monitoring job: {e}")
        
        # Add job to check price alerts every 6 hours
        _scheduler.add_job(
            run_price_monitoring,
            trigger=IntervalTrigger(hours=6),
            id='check_price_alerts',
            name='Monitor prices and trigger alerts',
            replace_existing=True,
        )
        
        # For development, add test job that runs every 5 minutes
        if os.getenv("ENVIRONMENT", "production") != "production":
            app_logger.info("🧪 Running in development mode - adding 5-minute test job")
            _scheduler.add_job(
                lambda: app_logger.info("✅ Scheduler test job running (5 min interval)"),
                trigger=IntervalTrigger(minutes=5),
                id='scheduler_test',
                name='Scheduler test job',
                replace_existing=True,
            )
        
        _scheduler.start()
        app_logger.info("✅ APScheduler started successfully")
        
    except Exception as error:
        app_logger.error(f"❌ Failed to start scheduler: {error}")
        raise


def stop_background_scheduler():
    """
    Stop the APScheduler background scheduler
    This is called from main.py on FastAPI shutdown
    """
    global _scheduler
    
    try:
        if _scheduler is None or not _scheduler.running:
            app_logger.warning("⚠️ Scheduler not running")
            return
        
        app_logger.info("⏹️ Stopping APScheduler...")
        _scheduler.shutdown(wait=True)
        _scheduler = None
        app_logger.info("✅ APScheduler stopped")
        
    except Exception as error:
        app_logger.error(f"❌ Error stopping scheduler: {error}")


def get_scheduler() -> Optional[BackgroundScheduler]:
    """Get the current scheduler instance"""
    return _scheduler


if __name__ == "__main__":
    # Run the scheduler
    # For testing, we use a 1-minute interval
    scheduler = PriceScheduler(interval_seconds=60)
    asyncio.run(scheduler.start())
