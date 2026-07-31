-- ==================== PLATFORMS TABLE ====================
CREATE TABLE IF NOT EXISTS platforms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  url VARCHAR(255) NOT NULL,
  logo_url VARCHAR(255),
  commission_rate DECIMAL(5, 2) DEFAULT 0.0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert common platforms
INSERT INTO platforms (name, url, logo_url, commission_rate) VALUES
('Amazon India', 'https://www.amazon.in', 'https://via.placeholder.com/50?text=Amazon', 5.0),
('Flipkart', 'https://www.flipkart.com', 'https://via.placeholder.com/50?text=Flipkart', 4.5),
('Croma', 'https://www.croma.com', 'https://via.placeholder.com/50?text=Croma', 3.0),
('Vijay Sales', 'https://www.vijaysales.com', 'https://via.placeholder.com/50?text=VijayS', 2.5),
('Best Buy', 'https://www.bestbuy.com', 'https://via.placeholder.com/50?text=BestBuy', 3.5),
('eBay India', 'https://www.ebay.in', 'https://via.placeholder.com/50?text=eBay', 4.0)
ON CONFLICT (name) DO NOTHING;

-- ==================== USERS TABLE ====================
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(20),
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  profile_image_url VARCHAR(255),
  
  -- Preferences
  preferred_platforms TEXT[], -- Array of platform IDs user prefers
  notification_enabled BOOLEAN DEFAULT TRUE,
  whatsapp_number VARCHAR(20),
  preferred_currency VARCHAR(10) DEFAULT 'INR',
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  verification_token VARCHAR(255),
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- ==================== CATEGORIES TABLE ====================
CREATE TABLE IF NOT EXISTS categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  icon_url VARCHAR(255),
  parent_category_id UUID REFERENCES categories(id),
  slug VARCHAR(100) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO categories (name, slug, description) VALUES
('Smartphones', 'smartphones', 'Mobile phones and smartphones'),
('Laptops', 'laptops', 'Laptop computers'),
('Tablets', 'tablets', 'Tablet devices'),
('Smart Watches', 'smartwatches', 'Wearable smart watches'),
('Headphones', 'headphones', 'Audio devices and headphones'),
('Cameras', 'cameras', 'Digital cameras'),
('Smart Home', 'smarthome', 'Smart home devices'),
('Gaming', 'gaming', 'Gaming devices and accessories')
ON CONFLICT (slug) DO NOTHING;

-- ==================== PRODUCTS TABLE ====================
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Product Info
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category_id UUID REFERENCES categories(id),
  
  -- Specifications
  brand VARCHAR(100),
  model VARCHAR(100),
  color VARCHAR(50),
  storage VARCHAR(50),
  ram VARCHAR(50),
  
  -- Images & Reviews
  image_url VARCHAR(255),
  additional_images TEXT[], -- Array of image URLs
  average_rating DECIMAL(3, 2),
  total_reviews INT DEFAULT 0,
  
  -- Deduplication
  unique_hash VARCHAR(255) UNIQUE, -- Hash to identify duplicate products
  canonical_name VARCHAR(255), -- Normalized product name
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT valid_rating CHECK (average_rating >= 0 AND average_rating <= 5)
);

CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_hash ON products(unique_hash);

-- ==================== PRODUCT PRICES TABLE ====================
-- This tracks price history for each product on each platform
CREATE TABLE IF NOT EXISTS product_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  platform_id UUID NOT NULL REFERENCES platforms(id),
  
  price DECIMAL(12, 2) NOT NULL,
  original_price DECIMAL(12, 2),
  discount_percent DECIMAL(5, 2),
  in_stock BOOLEAN DEFAULT TRUE,
  product_url VARCHAR(500) NOT NULL,
  rating DECIMAL(3, 2),
  reviews_count INT DEFAULT 0,
  
  -- Scraping metadata
  last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  scrape_source VARCHAR(100) -- 'amazon', 'flipkart', 'api', etc.
);

CREATE INDEX idx_product_prices_product ON product_prices(product_id);
CREATE INDEX idx_product_prices_platform ON product_prices(platform_id);
CREATE INDEX idx_product_prices_date ON product_prices(last_checked);
CREATE INDEX idx_product_prices_combo ON product_prices(product_id, platform_id);

-- ==================== WISHLISTS TABLE ====================
CREATE TABLE IF NOT EXISTS wishlists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100) DEFAULT 'My Wishlist',
  description TEXT,
  is_default BOOLEAN DEFAULT FALSE,
  is_public BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wishlists_user ON wishlists(user_id);

-- ==================== WISHLIST ITEMS TABLE ====================
CREATE TABLE IF NOT EXISTS wishlist_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wishlist_id UUID NOT NULL REFERENCES wishlists(id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(id),
  
  -- Price tracking
  price_when_added DECIMAL(12, 2),
  target_price DECIMAL(12, 2), -- Notify when price drops to this
  lowest_price_seen DECIMAL(12, 2),
  
  -- Status
  is_purchased BOOLEAN DEFAULT FALSE,
  purchase_date TIMESTAMP,
  purchase_platform_id UUID REFERENCES platforms(id),
  purchase_price DECIMAL(12, 2),
  
  -- Tracking
  price_drop_count INT DEFAULT 0,
  last_notified TIMESTAMP,
  
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wishlist_items_wishlist ON wishlist_items(wishlist_id);
CREATE INDEX idx_wishlist_items_product ON wishlist_items(product_id);
CREATE INDEX idx_wishlist_items_user ON wishlist_items(wishlist_id, is_purchased);

-- ==================== PRICE ALERTS TABLE ====================
CREATE TABLE IF NOT EXISTS price_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wishlist_item_id UUID NOT NULL REFERENCES wishlist_items(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id),
  
  previous_price DECIMAL(12, 2) NOT NULL,
  new_price DECIMAL(12, 2) NOT NULL,
  price_drop_amount DECIMAL(12, 2),
  price_drop_percent DECIMAL(5, 2),
  
  platform_id UUID REFERENCES platforms(id),
  product_url VARCHAR(500),
  
  notification_sent BOOLEAN DEFAULT FALSE,
  notification_method VARCHAR(50), -- 'whatsapp', 'email', 'both'
  notification_sent_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_alerts_user ON price_alerts(user_id);
CREATE INDEX idx_price_alerts_item ON price_alerts(wishlist_item_id);
CREATE INDEX idx_price_alerts_sent ON price_alerts(notification_sent);

-- ==================== PRICE PREDICTIONS TABLE ====================
CREATE TABLE IF NOT EXISTS price_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id),
  platform_id UUID REFERENCES platforms(id),
  
  predicted_price DECIMAL(12, 2),
  predicted_date DATE,
  confidence_percent DECIMAL(5, 2),
  recommendation VARCHAR(50), -- 'buy_now', 'wait_1_week', 'wait_2_weeks', etc.
  reason TEXT,
  
  model_version VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_product ON price_predictions(product_id);
CREATE INDEX idx_predictions_date ON price_predictions(predicted_date);

-- ==================== PURCHASES TABLE ====================
CREATE TABLE IF NOT EXISTS purchases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  product_id UUID NOT NULL REFERENCES products(id),
  platform_id UUID NOT NULL REFERENCES platforms(id),
  
  purchase_price DECIMAL(12, 2) NOT NULL,
  quantity INT DEFAULT 1,
  product_url VARCHAR(500),
  
  purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchases_user ON purchases(user_id);
CREATE INDEX idx_purchases_product ON purchases(product_id);
CREATE INDEX idx_purchases_date ON purchases(purchase_date);

-- ==================== SEARCH HISTORY TABLE ====================
CREATE TABLE IF NOT EXISTS search_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  search_query VARCHAR(255) NOT NULL,
  results_count INT,
  viewed_product_id UUID REFERENCES products(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_history_user ON search_history(user_id);
CREATE INDEX idx_search_history_date ON search_history(created_at);

-- ==================== REVIEWS TABLE ====================
CREATE TABLE IF NOT EXISTS reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id),
  user_id UUID NOT NULL REFERENCES users(id),
  
  rating DECIMAL(3, 2),
  title VARCHAR(255),
  comment TEXT,
  verified_purchase BOOLEAN DEFAULT FALSE,
  
  helpful_count INT DEFAULT 0,
  unhelpful_count INT DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);

-- ==================== ENABLE ROW LEVEL SECURITY ====================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;

-- ==================== RLS POLICIES ====================
-- Users can only see their own data
CREATE POLICY "users_select_policy" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_policy" ON users
  FOR UPDATE USING (auth.uid() = id);

-- Users can only see their own wishlists
CREATE POLICY "wishlists_select_policy" ON wishlists
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "wishlists_insert_policy" ON wishlists
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can only see their own wishlist items
CREATE POLICY "wishlist_items_select_policy" ON wishlist_items
  FOR SELECT USING (wishlist_id IN (SELECT id FROM wishlists WHERE user_id = auth.uid()));

-- Users can only see their own purchases
CREATE POLICY "purchases_select_policy" ON purchases
  FOR SELECT USING (auth.uid() = user_id);

-- ==================== FUNCTIONS ====================
-- Function to calculate price drop percentage
CREATE OR REPLACE FUNCTION calculate_price_drop_percent(previous_price DECIMAL, new_price DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
  IF previous_price = 0 THEN
    RETURN 0;
  END IF;
  RETURN ROUND(((previous_price - new_price) / previous_price * 100)::NUMERIC, 2);
END;
$$ LANGUAGE plpgsql;

-- Function to generate product unique hash
CREATE OR REPLACE FUNCTION generate_product_hash(product_name VARCHAR, brand VARCHAR, model VARCHAR, color VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
  RETURN MD5(LOWER(CONCAT(product_name, '-', COALESCE(brand, ''), '-', COALESCE(model, ''), '-', COALESCE(color, ''))));
END;
$$ LANGUAGE plpgsql;

-- ==================== INDEXES FOR PERFORMANCE ====================
CREATE INDEX idx_product_prices_best_deal ON product_prices(product_id, price DESC, in_stock);
CREATE INDEX idx_wishlists_user_default ON wishlists(user_id, is_default);

-- Schema created successfully!
-- All tables, indexes, and Row-Level Security policies are now ready.
