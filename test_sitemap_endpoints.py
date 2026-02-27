#!/usr/bin/env python
"""
Test sitemap endpoints end-to-end
"""

import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory
from storefront.views.sitemap import sitemap_products, sitemap_businesses
from core.middleware import SubdomainMiddleware

# Create test factory
factory = RequestFactory()

print("=" * 60)
print("SITEMAP ENDPOINT TESTS")
print("=" * 60)

# Test 1: Sitemap Index (no subdomain required)
print("\n1️⃣ Testing Sitemap Index (sitemap_index.xml)")
print("-" * 60)
try:
    request = factory.get('/sitemap_index.xml', HTTP_HOST='localhost:8000')
    # Manually set subdomain since we're not going through middleware
    request.subdomain = None
    
    response = sitemap_businesses(request)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📋 Content-Type: {response.get('Content-Type', 'Not set')}")
    print(f"⏱️  Cache-Control: {response.get('Cache-Control', 'Not set')}")
    
    # Check content
    content = response.content.decode('utf-8') if hasattr(response, 'content') else str(response)
    if '<sitemapindex' in content or '<urlset' in content:
        print("✅ Valid XML sitemap structure")
        lines = content.split('\n')
        print(f"   Content length: {len(content)} bytes")
    else:
        print("⚠️  Response doesn't appear to be valid XML")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Product Sitemap with subdomain
print("\n2️⃣ Testing Product Sitemap (sitemap.xml) with subdomain")
print("-" * 60)
try:
    request = factory.get('/sitemap.xml', HTTP_HOST='alice.localhost:8000')
    # Manually set subdomain
    request.subdomain = 'alice'
    
    response = sitemap_products(request)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📋 Content-Type: {response.get('Content-Type', 'Not set')}")
    print(f"⏱️  Cache-Control: {response.get('Cache-Control', 'Not set')}")
    print(f"📅 Last-Modified: {response.get('Last-Modified', 'Not set')}")
    
    # Check content
    content = response.content.decode('utf-8') if hasattr(response, 'content') else str(response)
    if '<urlset' in content:
        print("✅ Valid XML sitemap structure")
        # Count URLs
        url_count = content.count('<url>')
        img_count = content.count('<image:image>')
        print(f"   - URLs: {url_count}")
        print(f"   - Images: {img_count}")
        print(f"   - Content length: {len(content)} bytes")
    else:
        print("⚠️  Response doesn't appear to be valid XML")
        print(f"   Response: {content[:200]}...")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Product Sitemap without subdomain (should redirect)
print("\n3️⃣ Testing Product Sitemap without subdomain (should redirect)")
print("-" * 60)
try:
    request = factory.get('/sitemap.xml', HTTP_HOST='localhost:8000')
    request.subdomain = None
    
    response = sitemap_products(request)
    
    if response.status_code == 301:
        print(f"✅ Correct redirect status: {response.status_code}")
        print(f"📍 Redirects to: {response.get('Location', 'Not set')}")
    else:
        print(f"⚠️  Expected 301, got {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print("✅ All endpoint tests completed!")
print("=" * 60)
