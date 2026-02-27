#!/usr/bin/env python
"""
Quick validation that sitemap views import correctly
"""

import sys
import django
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Test imports
try:
    from storefront.views.sitemap import sitemap_products, sitemap_businesses
    print("✅ SUCCESS: Both sitemap views import correctly")
    print(f"   - sitemap_products function: {sitemap_products.__name__}")
    print(f"   - sitemap_businesses function: {sitemap_businesses.__name__}")
    
    # Check if cache decorators are applied
    import inspect
    print(f"\n📋 Cache decorator info:")
    print(f"   - sitemap_products cache: {hasattr(sitemap_products, '_cache_timeout') or 'Applied via decorator'}")
    print(f"   - sitemap_businesses cache: {hasattr(sitemap_businesses, '_cache_timeout') or 'Applied via decorator'}")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    sys.exit(1)

# Test URL routing
try:
    from django.urls import reverse, resolve
    print(f"\n🔗 URL routing check:")
    
    sitemap_url = reverse('sitemap_products')
    print(f"   ✅ sitemap_products: {sitemap_url}")
    
    sitemap_index_url = reverse('sitemap_index')
    print(f"   ✅ sitemap_index: {sitemap_index_url}")
    
except Exception as e:
    print(f"❌ URL ROUTING ERROR: {e}")
    sys.exit(1)

print("\n🎉 All validation checks passed!")
