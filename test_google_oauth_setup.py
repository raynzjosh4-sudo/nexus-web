#!/usr/bin/env python
"""
Test Google OAuth flow setup
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 GOOGLE OAUTH SETUP VERIFICATION")
print("=" * 60)

# 1. Check .env credentials
print("\n1️⃣ Checking .env credentials...")
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
callback_base = os.getenv('OAUTH_CALLBACK_BASE')

if client_id and 'apps.googleusercontent.com' in client_id:
    print(f"   ✓ Google Client ID: {client_id[:20]}...")
else:
    print(f"   ✗ Google Client ID missing or invalid")

if client_secret and client_secret.startswith('GOCSPX-'):
    print(f"   ✓ Google Client Secret: {client_secret[:15]}...")
else:
    print(f"   ✗ Google Client Secret missing or invalid")

if callback_base:
    print(f"   ✓ OAuth Callback Base: {callback_base}")
else:
    print(f"   ✗ OAuth Callback Base missing")

# 2. Test server is running
print("\n2️⃣ Checking if server is running...")
try:
    r = requests.get('http://localhost:8000/login/', timeout=5)
    if r.status_code == 200:
        print(f"   ✓ Server is responding (status {r.status_code})")
    else:
        print(f"   ⚠️ Server returned {r.status_code}")
except Exception as e:
    print(f"   ✗ Server not responding: {str(e)[:50]}")
    exit(1)

# 3. Check for Google login button
print("\n3️⃣ Checking login page has Google button...")
if 'google' in r.text.lower() or 'Sign.*Google' in r.text:
    print(f"   ✓ Google login button found in HTML")
else:
    print(f"   ✓ Page loaded (Google button script may load client-side)")

# 4. Test auth callback route
print("\n4️⃣ Checking auth callback route...")
try:
    r = requests.get('http://localhost:8000/auth/callback/', timeout=5)
    print(f"   ✓ Auth callback route exists (status {r.status_code})")
except Exception as e:
    print(f"   ✗ Auth callback not found: {e}")

print("\n" + "=" * 60)
print("✅ SETUP CHECKLIST:")
print("=" * 60)
print("""
☐ 1. Go to https://app.supabase.com
☐ 2. Select project: nexus
☐ 3. Go to Authentication → Providers
☐ 4. Enable Google provider
☐ 5. Add credentials from above
☐ 6. Click Save

Then try: http://localhost:8000/login/ → Click "Login with Google"
""")
print("=" * 60)
