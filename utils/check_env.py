from dotenv import load_dotenv
import os

load_dotenv()

checks = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
    "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY", ""),
    "COHERE_API_KEY": os.getenv("COHERE_API_KEY", ""),
    "REDIS_URL": os.getenv("REDIS_URL", ""),
}

for key, val in checks.items():
    is_set = bool(val) and "your_" not in val.lower() and val != ""
    masked = val[:8] + "..." if is_set and len(val) > 8 else "(not set)"
    print(f"{key}: {'YES' if is_set else 'NO'} [{masked}]")

# Test Supabase connection
if checks["SUPABASE_URL"] and "your_" not in checks["SUPABASE_URL"].lower():
    try:
        from supabase import create_client
        client = create_client(checks["SUPABASE_URL"], checks["SUPABASE_KEY"])
        result = client.table("platforms").select("name").limit(3).execute()
        print(f"\nSupabase connection: OK")
        print(f"Platforms in DB: {[p['name'] for p in result.data] if result.data else 'EMPTY - need to run migrations'}")
    except Exception as e:
        print(f"\nSupabase connection: FAILED - {e}")
else:
    print("\nSupabase: NOT CONFIGURED")
