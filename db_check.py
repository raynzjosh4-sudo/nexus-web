from storefront.client import get_supabase_client
import json

def check_db():
    supabase = get_supabase_client()
    
    print("--- Nexus Users ---")
    u_res = supabase.table('nexususers').select('id, name, email').limit(5).execute()
    print(json.dumps(u_res.data, indent=2))
    
    print("\n--- Market Orders (All) ---")
    o_res = supabase.table('market_orders').select('id, buyer_id, business_id, product_id').limit(5).execute()
    print(json.dumps(o_res.data, indent=2))
    
    print("\n--- Wishlists (All) ---")
    w_res = supabase.table('wishlists').select('user_id, product_id').limit(5).execute()
    print(json.dumps(w_res.data, indent=2))
    
    # Try to find a user with orders or wishes
    if o_res.data:
        test_uid = o_res.data[0]['buyer_id']
        print(f"\n--- Testing with user_id: {test_uid} (found in orders) ---")
        o_test = supabase.table('market_orders').select('*').eq('buyer_id', test_uid).execute()
        print(f"Orders found: {len(o_test.data)}")
        
    if w_res.data:
        test_uid = w_res.data[0]['user_id']
        print(f"\n--- Testing with user_id: {test_uid} (found in wishlists) ---")
        w_test = supabase.table('wishlists').select('*').eq('user_id', test_uid).execute()
        print(f"Wishes found: {len(w_test.data)}")

if __name__ == "__main__":
    check_db()
