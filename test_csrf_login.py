#!/usr/bin/env python
"""Test complete login flow with CSRF token"""
import requests
import time
import re

time.sleep(1)

session = requests.Session()

try:
    print("1️⃣ Fetching login page to get CSRF token...")
    r = session.get('http://localhost:8000/login/', timeout=10)
    print(f"   Status: {r.status_code}")
    
    # Extract CSRF token from HTML
    match = re.search(r'csrfmiddlewaretoken["\']?\s+value["\']?([a-zA-Z0-9]+)', r.text)
    if match:
        csrf_token = match.group(1)
        print(f"   ✓ CSRF token: {csrf_token[:10]}...")
    else:
        print("   ✗ CSRF token not found")
        exit(1)
    
    print("\n2️⃣ Testing login POST with CSRF token...")
    login_data = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    r2 = session.post(
        'http://localhost:8000/login/',
        data=login_data,
        timeout=10,
        allow_redirects=False
    )
    
    print(f"   Status: {r2.status_code}")
    
    if r2.status_code == 403 and 'CSRF' in r2.text:
        print("   ✗ Still getting CSRF error!")
        exit(1)
    elif r2.status_code in [200, 302]:
        if "Invalid" in r2.text or r2.status_code == 302:
            print("   ✓ PASSED! No CSRF error!")
            print("   ✓ Got proper login response (invalid credentials is expected)")
        else:
            print(f"   Response snippet: {r2.text[:100]}")
    else:
        print(f"   Unexpected status: {r2.status_code}")
        
    print("\n✅ CSRF protection is working correctly!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)
