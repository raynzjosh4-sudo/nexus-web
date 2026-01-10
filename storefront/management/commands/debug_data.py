from django.core.management.base import BaseCommand
from storefront.client import get_supabase_client
import json

class Command(BaseCommand):
    help = 'Inspect database records for debugging profile page'

    def handle(self, *args, **options):
        supabase = get_supabase_client()
        
        self.stdout.write(self.style.SUCCESS("--- Checking Database Records ---"))
        
        # Check nexususers
        self.stdout.write("\nChecking nexususers (first 3):")
        u_res = supabase.table('nexususers').select('id, name, email').limit(3).execute()
        self.stdout.write(json.dumps(u_res.data, indent=2))
        
        # Check market_orders
        self.stdout.write("\nChecking market_orders (first 3):")
        o_res = supabase.table('market_orders').select('id, buyer_id, product_id, status').limit(3).execute()
        self.stdout.write(json.dumps(o_res.data, indent=2))
        
        # Check wishlists
        self.stdout.write("\nChecking wishlists (first 3):")
        w_res = supabase.table('wishlists').select('user_id, product_id').limit(3).execute()
        self.stdout.write(json.dumps(w_res.data, indent=2))
        
        # Aggregates
        o_count = supabase.table('market_orders').select('id', count='exact').execute()
        w_count = supabase.table('wishlists').select('user_id', count='exact').execute()
        
        self.stdout.write(f"\nTotal market_orders in DB: {o_count.count}")
        self.stdout.write(f"Total wishlists in DB: {w_count.count}")
        
        if o_res.data:
            sample_uid = o_res.data[0]['buyer_id']
            self.stdout.write(self.style.WARNING(f"\nFound user with orders: {sample_uid}"))
            
        if w_res.data:
            sample_uid_w = w_res.data[0]['user_id']
            self.stdout.write(self.style.WARNING(f"Found user with wishes: {sample_uid_w}"))
