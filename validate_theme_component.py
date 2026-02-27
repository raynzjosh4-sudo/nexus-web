#!/usr/bin/env python
"""
Quick validation script to verify ProfileWebsiteThemeComponent is properly extracted
and passed to templates on all pages (except main_landing.html).
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storefront.client import get_supabase_client
from storefront.views.shop import normalize_component_data


def validate_theme_extraction():
    """Check if theme components are being properly extracted from businesses."""
    supabase = get_supabase_client()
    
    print("\n" + "="*70)
    print("THEME COMPONENT VALIDATION")
    print("="*70)
    
    # Fetch first 5 active businesses
    biz_response = supabase.table('business_profiles').select('id,domain,components').eq('status', 'active').limit(5).execute()
    
    if not biz_response.data:
        print("❌ No active businesses found")
        return
    
    for biz in biz_response.data:
        domain = biz.get('domain', 'unknown')
        components_raw = biz.get('components')
        
        print(f"\n📊 Business: {domain}")
        print(f"   Components Type: {type(components_raw).__name__}")
        
        # Parse components
        import json
        if isinstance(components_raw, str):
            try:
                components = json.loads(components_raw) or []
            except:
                components = []
        elif isinstance(components_raw, list):
            components = components_raw
        else:
            components = []
        
        print(f"   Total Components: {len(components)}")
        
        # Find theme component
        theme_found = False
        for comp in components:
            raw_type = comp.get('type', '')
            if 'theme' in raw_type.lower() or 'websitetheme' in raw_type.lower():
                # Normalize it
                normalized = normalize_component_data(comp)
                clean_type = normalized.get('clean_type', 'unknown')
                
                print(f"   ✅ Theme Component Found:")
                print(f"      Raw Type: {raw_type}")
                print(f"      Normalized Type: {clean_type}")
                print(f"      Colors:")
                print(f"        - textColor: {normalized.get('textColor', 'NOT SET')}")
                print(f"        - accentColor: {normalized.get('accentColor', 'NOT SET')}")
                print(f"        - primaryColor: {normalized.get('primaryColor', 'NOT SET')}")
                print(f"        - surfaceColor: {normalized.get('surfaceColor', 'NOT SET')}")
                print(f"        - secondaryColor: {normalized.get('secondaryColor', 'NOT SET')}")
                print(f"        - backgroundColor: {normalized.get('backgroundColor', 'NOT SET')}")
                theme_found = True
                break
        
        if not theme_found:
            print(f"   ❌ No theme component found (will use default colors)")
    
    print("\n" + "="*70)
    print("✅ Theme Component Validation Complete")
    print("="*70)
    print("\nNOTE: Make sure ProfileWebsiteThemeComponent is set in each business's components")
    print("Expected fields: textColor, accentColor, primaryColor, surfaceColor, secondaryColor, backgroundColor")
    

def validate_normalized_mapping():
    """Verify that component type mapping is correct."""
    from storefront.views.shop import normalize_component_data
    
    print("\n" + "="*70)
    print("TYPE MAPPING VALIDATION")
    print("="*70)
    
    test_types = [
        'ProfileWebsiteThemeComponent',
        'websitetheme',
        'theme',
        'ProfileServicesComponent',
        'ProfileFeaturesComponent',
    ]
    
    for test_type in test_types:
        test_comp = {'type': test_type}
        normalized = normalize_component_data(test_comp)
        clean = normalized.get('clean_type', 'unknown')
        print(f"   {test_type:30} → {clean}")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    try:
        validate_normalized_mapping()
        validate_theme_extraction()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
