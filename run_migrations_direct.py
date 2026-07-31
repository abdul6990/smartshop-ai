"""
Simple Database Migration Runner
Execute SQL migrations on Supabase PostgreSQL database
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Use direct PostgreSQL connection string
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("🚀 DATABASE MIGRATION RUNNER")
print("=" * 60)

# Method 1: Using psycopg2 (PostgreSQL driver)
try:
    import psycopg2
    print("\n✅ psycopg2 found - using direct PostgreSQL connection")
    
    # Extract connection details from Supabase URL
    # Format: https://project.supabase.co
    project_id = SUPABASE_URL.split("//")[1].split(".")[0]
    
    # Standard Supabase PostgreSQL connection
    conn = psycopg2.connect(
        host=f"{project_id}.db.supabase.co",
        database="postgres",
        user="postgres",
        password=SUPABASE_KEY,
        port=5432,
        sslmode="require"
    )
    cursor = conn.cursor()
    
    print(f"📍 Connecting to: {project_id}.db.supabase.co")
    print("✅ Connection successful!\n")
    
    # Read migration file
    migration_file = "migrations/001_create_schema.sql"
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        exit(1)
    
    print(f"📂 Reading migration: {migration_file}")
    
    with open(migration_file, 'r') as f:
        sql_content = f.read()
    
    # Execute migration
    print("🔄 Executing migration...")
    print("-" * 60)
    
    try:
        cursor.execute(sql_content)
        conn.commit()
        
        print("-" * 60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("\n📊 Tables created:")
        
        # List all created tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        for i, (table_name,) in enumerate(tables, 1):
            print(f"  {i}. {table_name}")
        
        print(f"\n✅ Total tables: {len(tables)}")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
        exit(1)
    
    finally:
        cursor.close()
        conn.close()

# Method 2: If psycopg2 not available, show manual instructions
except ImportError:
    print("⚠️ psycopg2 not installed")
    print("\nOPTION 1: Install psycopg2 and re-run")
    print("  $ pip install psycopg2-binary")
    print("  $ python run_migrations_direct.py")
    
    print("\nOPTION 2: Manual migration (Recommended for first time)")
    print("\n" + "=" * 60)
    print("MANUAL MIGRATION STEPS:")
    print("=" * 60)
    
    print("\n1️⃣ Go to Supabase Dashboard:")
    print("   https://supabase.com/dashboard")
    
    print("\n2️⃣ Select your project")
    
    print("\n3️⃣ Go to SQL Editor (left sidebar)")
    
    print("\n4️⃣ Create new query")
    
    print("\n5️⃣ Copy-paste the SQL from: migrations/001_create_schema.sql")
    
    print("\n6️⃣ Click 'Run' or press Ctrl+Enter")
    
    print("\n7️⃣ Wait for completion (1-2 seconds)")
    
    print("\n✅ Done! All tables created")
    
    print("\n" + "=" * 60)
    print("Or install psycopg2 and run automated migration:")
    print("$ pip install psycopg2-binary")
    print("$ python run_migrations_direct.py")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)
