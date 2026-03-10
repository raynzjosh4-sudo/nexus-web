#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storefront.client import get_supabase_client
from datetime import datetime

supabase = get_supabase_client()

# Check all business profiles
print("=== ALL BUSINESS PROFILES ===")
all_biz = supabase.table('business_profiles').select('id,domain,status,business_name').execute()
print(f"Total businesses: {len(all_biz.data) if all_biz.data else 0}")
for b in (all_biz.data or [])[:10]:
    print(f"  {b.get('business_name'):20} | Domain: {b.get('domain'):15} | Status: {b.get('status')}")

# Check active businesses only
print("\n=== ACTIVE BUSINESSES ===")
active = supabase.table('business_profiles').select('id,domain,status,updated_at').eq('status', 'active').execute()
print(f"Active businesses: {len(active.data) if active.data else 0}")
for b in (active.data or [])[:5]:
    print(f"  Domain: {b.get('domain')}, Updated: {b.get('updated_at')}")

# Show what the sitemap index would generate
print("\n=== SITEMAP INDEX ENTRIES ===")
sitemaps = []
for biz in (active.data or []):
    domain = biz.get('domain')
    if domain:
        sitemaps.append({
            'loc': f"https://{domain}.nexassearch.com/sitemap.xml",
            'lastmod': biz.get('updated_at', datetime.now().strftime('%Y-%m-%d'))[:10] if biz.get('updated_at') else datetime.now().strftime('%Y-%m-%d'),
        })

if sitemaps:
    print(f"Would generate {len(sitemaps)} sitemap entries:")
    for sm in sitemaps[:3]:
        print(f"  - {sm['loc']} (Updated: {sm['lastmod']})")
else:
    print("NO SITEMAP ENTRIES - This is the problem!")
