import os
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Manually load env for this standalone check
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check():
    print("--- Nexus Users ---")
    u = supabase.table('nexususers').select('id, name, email').limit(5).execute()
    print(json.dumps(u.data, indent=2))
    
    print("\n--- Market Orders ---")
    o = supabase.table('market_orders').select('id, buyer_id, business_id, product_id, status').limit(5).execute()
    print(json.dumps(o.data, indent=2))
    
    print("\n--- Wishlists ---")
    w = supabase.table('wishlists').select('user_id, product_id').limit(5).execute()
    print(json.dumps(w.data, indent=2))

if __name__ == "__main__":
    check()
