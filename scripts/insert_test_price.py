from utils.supabase_client import db
import uuid

PRODUCT_ID = 'b90a5702-edc9-4cfd-9ce3-1698e941f863'
TEST_PRICE = 149900.00
TEST_URL = 'https://www.amazon.in/dp/test-product'

if not db.is_connected:
    print('Supabase client not connected. Check SUPABASE_URL and SUPABASE_KEY env vars')
    raise SystemExit(1)

# Find Amazon India platform id
platforms = db.table('platforms').select('id,name').eq('name','Amazon India').limit(1).execute()
if not platforms.data:
    print('Amazon platform not found; dumping platforms list:')
    allp = db.table('platforms').select('id,name').execute()
    print(allp.data)
    raise SystemExit(1)

platform_id = platforms.data[0]['id']

row = {
    'product_id': PRODUCT_ID,
    'platform_id': platform_id,
    'price': TEST_PRICE,
    'original_price': TEST_PRICE,
    'discount_percent': 0,
    'in_stock': True,
    'product_url': TEST_URL,
    'rating': 4.5,
    'reviews_count': 10,
    'scrape_source': 'dev_test'
}

res = db.table('product_prices').insert(row).execute()
print('Insert result:', res.data or res.error)
