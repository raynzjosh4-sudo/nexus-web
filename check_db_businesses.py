#!/usr/bin/env python
"""Check database for businesses"""

import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from storefront.client import get_supabase_client

supabase = get_supabase_client()
biz = supabase.table('business_profiles').select('id,domain,status').limit(5).execute()

print("Businesses in database:")
for b in biz.data:
    print(f"  • {b.get('domain')} (status: {b.get('status')})")
print(f"\nTotal retrieved: {len(biz.data)}")
