#!/usr/bin/env python
import requests
import re

link = requests.get('http://localhost:8000/login/', timeout=5)
# Check if there's a '/None' href in the HTML
if '/None' in link.text:
    print('✗ Found /None in HTML!')
    matches = re.findall(r'href=["\']([^"\']*None[^"\']*)', link.text)
    for m in matches:
        print(f'  >> {m}')
else:
    print('✓ No /None found in login page HTML')

# Check for onclick or action
if '/None' in link.text or 'None' in link.text:
    # Find all occurrences in context
    lines = link.text.split('\n')
    for i, line in enumerate(lines):
        if 'None' in line and ('href' in line or 'action' in line or 'onclick' in line):
            print(f'Line {i}: {line.strip()[:100]}')
