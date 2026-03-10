#!/usr/bin/env python
import urllib.request

try:
    req = urllib.request.Request('http://localhost:8000/sitemap_index.xml')
    response = urllib.request.urlopen(req, timeout=5)
    
    print("=== RESPONSE HEADERS ===")
    for header, value in response.headers.items():
        print(f"{header}: {value}")
    
    print("\n=== RESPONSE CONTENT (first 1500 chars) ===\n")
    content = response.read().decode('utf-8')
    print(content[:1500])
    
    print(f"\n... (total {len(content)} bytes)\n")
    
    # Check for issues
    print("=== VALIDATION ===")
    print(f"✓ Contains opening <sitemapindex>: {'<sitemapindex' in content}")
    print(f"✓ Contains closing </sitemapindex>: {'</sitemapindex>' in content}")
    print(f"✓ Contains <sitemap> tags: {'<sitemap>' in content}")
    print(f"✓ Number of <sitemap> entries: {content.count('<sitemap>')}")
    
    # Try parsing as XML
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(content)
        print(f"✓ Valid XML: Yes")
        print(f"✓ Root tag: {root.tag}")
        
        ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemaps = root.findall('sitemap:sitemap', ns)
        if not sitemaps:
            # Try without namespace
            sitemaps = root.findall('sitemap')
        print(f"✓ Found {len(sitemaps)} sitemap elements")
    except Exception as e:
        print(f"✗ XML parsing error: {e}")
            
except Exception as e:
    print(f"Error: {e}")
