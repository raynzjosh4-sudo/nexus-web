#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storefront.views.sitemap_index import sitemap_index
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/sitemap_index.xml', HTTP_HOST='nexassearch.com')
request.subdomain = None  # Root domain request
response = sitemap_index(request)

# Get the XML content
xml_content = response.content.decode('utf-8')
print('=== SITEMAP INDEX XML ===\n')
print(xml_content[:1500])
print(f'\n... (truncated)\n')
print(f'Total length: {len(xml_content)} bytes')
print(f'Contains <sitemap> tags: {"<sitemap>" in xml_content}')
print(f'Number of <sitemap> entries: {xml_content.count("<sitemap>")}')

# Validate it's valid XML
import xml.etree.ElementTree as ET
try:
    root = ET.fromstring(xml_content)
    print(f'XML is valid!')
    print(f'Root tag: {root.tag}')
    sitemaps = root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
    print(f'Number of sitemap elements: {len(sitemaps)}')
    for i, sm in enumerate(sitemaps[:3]):
        loc = sm.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        lastmod = sm.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
        print(f'  [{i+1}] {loc.text if loc is not None else "NO LOC"} (Updated: {lastmod.text if lastmod is not None else "NO DATE"})')
except Exception as e:
    print(f'XML parsing error: {e}')
