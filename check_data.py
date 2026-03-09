#!/usr/bin/env python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
django.setup()
from storefront.client import get_supabase_client
import json

supabase = get_supabase_client()

print("=" * 70)
print("BUSINESS DATA HEALTH CHECK")
print("=" * 70)

# Get all businesses
biz = supabase.table('business_profiles').select('*').execute()
print(f"\nTotal businesses in database: {len(biz.data)}\n")

# Count by status
status_count = {}
for b in biz.data:
    status = b.get('status', 'unknown')
    status_count[status] = status_count.get(status, 0) + 1

print("Business Status Distribution:")
for status, count in sorted(status_count.items()):
    print(f"  {status.upper()}: {count}")

print("\n" + "=" * 70)
print("DETAILED BUSINESS ANALYSIS")
print("=" * 70)

for i, b in enumerate(biz.data[:5]):  # Check first 5
    print(f"\n[Business {i+1}]")
    print(f"  Name: {b.get('business_name', 'N/A')}")
    print(f"  Domain: {b.get('domain', 'N/A')}")
    print(f"  Status: {b.get('status', 'N/A')}")
    print(f"  URL: https://{b.get('domain', 'N/A')}.nexassearch.com/")
    print(f"  Logo: {b.get('logo_url', 'N/A')[:50]}...")
    print(f"  Description: {(b.get('business_description') or 'N/A')[:60]}...")
    print(f"  Category: {b.get('category', 'N/A')}")
    print(f"  Address: {b.get('business_address', 'N/A')}")
    print(f"  Phone: {b.get('business_phone_number', 'N/A')}")
    
    # Check components
    components_raw = b.get('components', [])
    if isinstance(components_raw, str):
        try:
            components_raw = json.loads(components_raw)
        except:
            components_raw = []
    print(f"  Components: {len(components_raw)} found")
    if components_raw:
        comp_types = set()
        for c in components_raw[:3]:
            if isinstance(c, dict):
                comp_types.add(c.get('type', 'unknown'))
        print(f"    Types: {', '.join(comp_types)}")
    
    # Check product count for each business
    posts = supabase.table('posts').select('id').eq('business_id', b['id']).execute()
    print(f"  Products: {len(posts.data)}")

print("\n" + "=" * 70)
print("ACTIVE BUSINESSES THAT SHOULD BE IN SITEMAPS")
print("=" * 70)

active_biz = [b for b in biz.data if b.get('status') == 'active']
print(f"\nActive businesses: {len(active_biz)}\n")

for b in active_biz:
    posts = supabase.table('posts').select('id').eq('business_id', b['id']).execute()
    print(f"✅ {b.get('business_name')} ({b.get('domain')}) - {len(posts.data)} products")
