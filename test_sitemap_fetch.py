#!/usr/bin/env python
import urllib.request
import urllib.error

try:
    response = urllib.request.urlopen('http://localhost:8000/sitemap_index.xml', timeout=5)
    xml_content = response.read().decode('utf-8')
    
    print('=== SITEMAP INDEX XML (first 2000 chars) ===\n')
    print(xml_content[:2000])
    print('\n. . .\n')
    
    print(f'Total XML size: {len(xml_content)} bytes')
    print(f'Contains <sitemap> tags: {"<sitemap>" in xml_content}')
    print(f'Number of <sitemap> entries: {xml_content.count("<sitemap>")}')
    
    # Show all sitemap entries
    import re
    sitemaps = re.findall(r'<sitemap>.*?</sitemap>', xml_content, re.DOTALL)
    print(f'\nFound {len(sitemaps)} entries:')
    for i, sm in enumerate(sitemaps[:5], 1):
        loc = re.search(r'<loc>(.*?)</loc>', sm)
        if loc:
            print(f'  [{i}] {loc.group(1)}')
            
except Exception as e:
    print(f'Error: {e}')
