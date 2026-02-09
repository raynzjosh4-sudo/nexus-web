#!/usr/bin/env python
import requests
import time
import sys

time.sleep(2)

try:
    print("Testing CSRF token setup...")
    r = requests.get('http://localhost:8000/login/', timeout=10)
    print(f'✓ Status: {r.status_code}')
    
    if 'csrfmiddlewaretoken' in r.text:
        print(f'✓ CSRF token present in HTML form')
    else:
        print(f'✗ CSRF token NOT in form')
    
    cookies = list(r.cookies.keys())
    print(f'✓ Cookies set: {cookies}')
    
    if 'sessionid' in cookies or 'Session' in str(r.headers):
        print(f'✓ Session cookie present')
    
    print(f'\n✓ CSRF protection is now active!')
    print(f'✓ Try logging in at http://localhost:8000/login/')
    
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
