#!/usr/bin/env python
"""Verify all Supabase tables are accessible"""

from storefront.client import get_supabase_client

supabase = get_supabase_client()
print("✓ Supabase client initialized\n")

# Define expected tables
tables = {
    'community_posts': 'Community Discussion Posts',
    'lost_found_items': 'Lost & Found Items',
    'swap_items': 'Swap/Trade Items',
    'nexususers': 'User Profiles',
    'business_profiles': 'Business Profiles',
    'posts': 'Products/Posts',
    'categories': 'Categories',
}

print("Checking table accessibility:\n")
all_good = True

for table_name, description in tables.items():
    try:
        result = supabase.table(table_name).select('id').limit(1).execute()
        count = len(result.data)
        status = f"✓ {count} record(s) found"
        print(f"  {table_name:25} ({description:30}) {status}")
    except Exception as e:
        all_good = False
        error = str(e)[:40]
        print(f"  {table_name:25} ({description:30}) ✗ ERROR: {error}")

print("\n" + "="*80)
if all_good:
    print("✅ SUCCESS: All Supabase tables are ready!")
    print("\nTable mappings for SEO views:")
    print("  community_posts      → DiscussionForumPosting schema")
    print("  lost_found_items     → Article schema")
    print("  swap_items           → Product schema")
    print("  nexususers           → ProfilePage schema (user profiles)")
    print("  business_profiles    → LocalBusiness schema")
    print("  posts                → Product listings")
else:
    print("⚠️  Some tables are not accessible. Check Supabase connection.")
print("="*80)
