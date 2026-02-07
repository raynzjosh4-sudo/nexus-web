#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storefront.client import get_supabase_client

supabase = get_supabase_client()

# Check what statuses exist
response = supabase.table('business_profiles').select('domain,status,id').limit(100).execute()

if response.data:
    statuses = {}
    for business in response.data:
        status = business.get('status', 'unknown')
        statuses[status] = statuses.get(status, 0) + 1
    
    print("\nBusiness Status Distribution:")
    print("=" * 50)
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")
    
    print("\nSample businesses (first 10):")
    print("=" * 50)
    for i, business in enumerate(response.data[:10], 1):
        print(f"{i}. Domain: {business['domain']}")
        print(f"   Status: {business.get('status', 'no status')}")
        print(f"   ID: {business['id'][:8]}...")
        
        # Check if this business has products
        posts = supabase.table('posts').select('id').eq('business_id', business['id']).execute()
        print(f"   Products: {len(posts.data)}")
        print()
else:
    print("❌ No businesses found in database")

print("\nFor sitemap generation to work, businesses need status='published'")
print("Check if status column uses different values (active, live, draft, etc.)")
