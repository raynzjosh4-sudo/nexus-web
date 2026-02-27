#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storefront.client import get_supabase_client
from storefront.views.product import get_theme_component
import json

supabase = get_supabase_client()

# Check loom business profile
response = supabase.table('business_profiles').select('*').eq('domain', 'loom').execute()
if response.data:
    biz = response.data[0]
    print("✓ Business found: loom")
    print(f"Business data keys: {biz.keys()}")
    components_raw = biz.get('components')
    print(f"\nRaw components type: {type(components_raw)}")
    print(f"Raw components: {components_raw}")
    
    if isinstance(components_raw, str):
        try:
            components = json.loads(components_raw)
            print(f"\n✓ Parsed components ({len(components)} items):")
            for i, c in enumerate(components):
                print(f"  [{i}] type={c.get('type', 'unknown')}, keys={list(c.keys())}")
        except Exception as e:
            print(f"  ✗ Failed to parse: {e}")
    
    # Now test get_theme_component
    print("\n--- Testing get_theme_component ---")
    theme = get_theme_component(biz)
    if theme:
        print(f"✓ Theme found: {json.dumps(theme, indent=2)}")
    else:
        print("✗ Theme component not found")
else:
    print("✗ Business 'loom' not found in database")
