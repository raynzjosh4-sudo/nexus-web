#!/usr/bin/env python
import os
import sys
import django
from django.test.utils import setup_test_environment

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.getcwd())
django.setup()

# Now render the theme_css.html template
from django.template.loader import render_to_string

ctx = {'theme_component': None}
try:
    html = render_to_string('storefront/theme_css.html', ctx)
    # Check for malformed braces in CSS
    if '--bg-page: {' in html:
        print('ERROR: Malformed template tags still present')
        print(html[:500])
    else:
        print('SUCCESS: Template renders cleanly')
        # Show first few CSS lines
        lines = [l for l in html.split('\n') if '--' in l and ':' in l][:5]
        for line in lines:
            print(line.strip())
except Exception as e:
    print(f'ERROR: {e}')
