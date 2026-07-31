-- ==================== DISABLE RLS POLICIES ====================
-- Temporarily disable RLS to allow backend initialization
-- We'll use JWT authentication instead of Supabase Auth

ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE wishlists DISABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE purchases DISABLE ROW LEVEL SECURITY;
ALTER TABLE search_history DISABLE ROW LEVEL SECURITY;

-- Important: Production should use Supabase Auth with proper RLS policies
-- For now, we rely on JWT tokens in the FastAPI backend for security

-- RLS policies disabled for development
-- All table access is controlled via JWT middleware in FastAPI
