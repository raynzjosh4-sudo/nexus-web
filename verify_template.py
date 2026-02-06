#!/usr/bin/env python
import os
import sys
import django

# Setup Django  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.getcwd())
django.setup()

# Render the template like the view does
from django.template.loader import render_to_string

ctx = {
    'business': {
        'business_name': 'Chill & Press',
        'theme_component': None,  # Simulate None like shop home might pass
    },
    'theme_component': None,
    'hero_component': None,
    'tab_component': None,
    'components': [],
    'products_by_category': {},
    'search_query': '',
}

try:
    html = render_to_string('storefront/shop_home.html', ctx)
    print('✓ SUCCESS: Template rendered without errors')
    print(f'✓ Page length: {len(html)} bytes')
except Exception as e:
    print(f'✗ ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
