#!/usr/bin/env python
"""
Google OAuth Configuration Diagnostic
Checks if everything is properly set up for Google login
"""

import os
import sys
from pathlib import Path

print("\n" + "="*80)
print("🔍 GOOGLE OAUTH CONFIGURATION DIAGNOSTIC")
print("="*80 + "\n")

# Check .env
print("1️⃣  Checking .env file...")
print("-" * 80)

env_file = Path('.env')
if env_file.exists():
    print("✓ .env file found\n")
    with open('.env') as f:
        content = f.read()
        
    checks = {
        'GOOGLE_CLIENT_ID': 'Google Client ID',
        'GOOGLE_CLIENT_SECRET': 'Google Client Secret',
        'OAUTH_CALLBACK_BASE': 'OAuth Callback Base URL',
        'SUPABASE_URL': 'Supabase URL',
        'SUPABASE_KEY': 'Supabase API Key',
    }
    
    for key, description in checks.items():
        if key in content:
            # Get the value (not showing full secrets)
            lines = [line for line in content.split('\n') if line.startswith(key)]
            if lines:
                value = lines[0].split('=')[1].strip().strip('"').strip("'")
                if len(value) > 30:
                    show_value = value[:20] + "..." + value[-10:]
                else:
                    show_value = value
                print(f"  ✓ {key:25} = {show_value}")
            else:
                print(f"  ✗ {key:25} = (empty)")
        else:
            print(f"  ✗ {key:25} = (NOT SET)")
else:
    print("✗ .env file NOT found!")
    print("  Create a .env file with your credentials\n")

# Check Django settings
print("\n2️⃣  Checking Django settings...")
print("-" * 80)

from django.conf import settings
import django

try:
    django.setup()
    print("✓ Django configured\n")
    
    settings_to_check = {
        'DEBUG': settings.DEBUG,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'INSTALLED_APPS': 'storefront' in settings.INSTALLED_APPS,
    }
    
    print(f"  DEBUG mode: {'✓ ON' if settings.DEBUG else '✗ OFF (production settings active)'}")
    print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:2]}...")  # Show first 2
    
except Exception as e:
    print(f"✗ Django setup error: {e}\n")

# Check URLs
print("\n3️⃣  Checking URL routes...")
print("-" * 80)

from storefront.urls import urlpatterns as storefront_urls

auth_routes = {
    'login/': False,
    'login/google/': False,
    'auth/callback/': False,
    'signup/': False,
    'logout/': False,
}

for pattern in storefront_urls:
    pattern_str = str(pattern.pattern)
    for route in auth_routes.keys():
        if route in pattern_str:
            auth_routes[route] = True

print(f"  ✓ Login route: {auth_routes.get('login/', '✗')}")
print(f"  ✓ Google login: {auth_routes.get('login/google/', '✗')}")
print(f"  ✓ OAuth callback: {auth_routes.get('auth/callback/', '✗')}")
print(f"  ✓ Signup route: {auth_routes.get('signup/', '✗')}")
print(f"  ✓ Logout route: {auth_routes.get('logout/', '✗')}")

# Check Supabase
print("\n4️⃣  Checking Supabase connection...")
print("-" * 80)

try:
    from storefront.client import get_supabase_client
    supabase = get_supabase_client()
    
    # Try to make a simple query
    result = supabase.table('community_posts').select('COUNT()').limit(1).execute()
    print("✓ Supabase connected successfully\n")
except Exception as e:
    print(f"✗ Supabase connection error: {str(e)[:60]}\n")

# Summary
print("\n" + "="*80)
print("📋 SUMMARY & NEXT STEPS")
print("="*80 + "\n")

issues = []

if not env_file.exists():
    issues.append("Create .env file with Google OAuth credentials")

env_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'OAUTH_CALLBACK_BASE']
if env_file.exists():
    with open('.env') as f:
        env_content = f.read()
    for var in env_vars:
        if var not in env_content or f"{var}=" not in env_content:
            issues.append(f"Add {var} to .env file")

if issues:
    print("⚠️  MISSING CONFIGURATION:\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    print("\n📖 Read: GOOGLE_OAUTH_SETUP.md for detailed instructions")
else:
    print("✅ All OAuth settings appear to be configured!")
    print("\n🧪 To test:")
    print("  1. Start server: python manage.py runserver 0.0.0.0:8000")
    print("  2. Visit: http://loom.localhost:8000/login/")
    print("  3. Click 'Login with Google'")
    print("  4. If redirected to Google login, OAuth is working!")

print("\n" + "="*80)
print("Need help? Check GOOGLE_OAUTH_SETUP.md\n")
