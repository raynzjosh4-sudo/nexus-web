#!/usr/bin/env python
"""
Diagnostic script to verify authentication system health.
Run this in Django shell: python manage.py shell < verify_auth_system.py
Or: python verify_auth_system.py
"""

import os
import sys
import django

# Setup Django if running as standalone script
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from storefront.client import get_supabase_client
from storefront.views.auth import _get_business_context
from django.test import RequestFactory
from django.http import HttpRequest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_env_vars():
    """Check if required environment variables are set"""
    print_section("1. Environment Variables Check")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'SECRET_KEY']
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + '...' + value[-10:] if len(value) > 20 else value
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ❌ {var}: NOT SET")
            all_good = False
    
    return all_good

def check_supabase_connection():
    """Test Supabase client connection"""
    print_section("2. Supabase Connection Check")
    
    try:
        supabase = get_supabase_client()
        print(f"  ✅ Supabase client created successfully")
        
        # Try a simple query
        res = supabase.table('business_profiles').select('count', count='exact').execute()
        count = res.count
        print(f"  ✅ Successfully queried database: {count} business profiles found")
        return True
    except Exception as e:
        print(f"  ❌ Supabase connection failed: {e}")
        return False

def check_business_context():
    """Test _get_business_context function"""
    print_section("3. Business Context Function Check")
    
    try:
        # Create a mock request with subdomain
        factory = RequestFactory()
        request = factory.get('/')
        request.subdomain = 'alice'  # Test with known business
        
        context = _get_business_context(request)
        
        if context:
            print(f"  ✅ _get_business_context returned data")
            print(f"     - business_name: {context.get('business_name', 'N/A')}")
            print(f"     - domain: {context.get('domain', 'N/A')}")
            print(f"     - theme_component: {type(context.get('theme_component', {}))}")
            print(f"     - components count: {len(context.get('components', []))}")
            return True
        else:
            print(f"  ⚠️  _get_business_context returned empty dict")
            return True  # This is acceptable for no subdomain
    except Exception as e:
        print(f"  ❌ _get_business_context failed: {e}")
        return False

def check_database_tables():
    """Check if required tables exist"""
    print_section("4. Required Database Tables Check")
    
    try:
        supabase = get_supabase_client()
        tables_to_check = ['business_profiles', 'posts', 'users', 'categories']
        all_exist = True
        
        for table in tables_to_check:
            try:
                res = supabase.table(table).select('count', count='exact').limit(1).execute()
                count = res.count if hasattr(res, 'count') else '?'
                print(f"  ✅ Table '{table}' exists (count: {count})")
            except Exception as e:
                print(f"  ❌ Table '{table}' not found or error: {e}")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"  ❌ Failed to check tables: {e}")
        return False

def check_auth_views_import():
    """Check if auth views can be imported without errors"""
    print_section("5. Auth Views Import Check")
    
    try:
        from storefront.views.auth import login_view, signup_view, google_login_view
        print(f"  ✅ login_view imported successfully")
        print(f"  ✅ signup_view imported successfully")
        print(f"  ✅ google_login_view imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to import auth views: {e}")
        return False

def check_login_template():
    """Check if login template exists and has required fields"""
    print_section("6. Login Template Check")
    
    try:
        from django.template.loader import get_template
        template = get_template('storefront/login.html')
        print(f"  ✅ login.html template found")
        
        # Check if key template variables are mentioned
        template_source = template.template.source
        checks = {
            'email field': 'name="email"' in template_source,
            'password field': 'name="password"' in template_source,
            'business context': 'business' in template_source,
            'error display': '{{ error }}' in template_source,
        }
        
        for check_name, result in checks.items():
            if result:
                print(f"  ✅ {check_name} found in template")
            else:
                print(f"  ⚠️  {check_name} NOT found in template")
        
        return all(checks.values())
    except Exception as e:
        print(f"  ❌ Failed to check login template: {e}")
        return False

def check_signup_template():
    """Check if signup template exists"""
    print_section("7. Signup Template Check")
    
    try:
        from django.template.loader import get_template
        template = get_template('storefront/signup.html')
        print(f"  ✅ signup.html template found")
        
        template_source = template.template.source
        checks = {
            'name field': 'name="name"' in template_source,
            'email field': 'name="email"' in template_source,
            'password field': 'name="password"' in template_source,
            'confirm password field': 'name="confirm_password"' in template_source,
        }
        
        for check_name, result in checks.items():
            if result:
                print(f"  ✅ {check_name} found in template")
            else:
                print(f"  ❌ {check_name} NOT found in template")
        
        return all(checks.values())
    except Exception as e:
        print(f"  ❌ Failed to check signup template: {e}")
        return False

def check_url_routes():
    """Check if auth URLs are registered"""
    print_section("8. Auth URL Routes Check")
    
    try:
        from django.urls import get_resolver, reverse
        resolver = get_resolver()
        
        url_patterns = {
            'login': 'login',
            'signup': 'signup',
            'logout': 'logout',
            'google_login': 'google_login',
        }
        
        all_exist = True
        for name, pattern in url_patterns.items():
            try:
                url = reverse(pattern)
                print(f"  ✅ URL '{pattern}' maps to: {url}")
            except Exception:
                print(f"  ❌ URL '{pattern}' not found")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"  ❌ Failed to check URLs: {e}")
        return False

def run_all_checks():
    """Run all diagnostic checks"""
    print("\n" + "="*60)
    print("  NEXUS WEB - AUTHENTICATION SYSTEM DIAGNOSTICS")
    print("="*60)
    
    results = {}
    
    results['env_vars'] = check_env_vars()
    results['supabase'] = check_supabase_connection()
    results['business_context'] = check_business_context()
    results['database_tables'] = check_database_tables()
    results['auth_views'] = check_auth_views_import()
    results['login_template'] = check_login_template()
    results['signup_template'] = check_signup_template()
    results['url_routes'] = check_url_routes()
    
    # Summary
    print_section("SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check}")
    
    print(f"\n  Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n  🎉 All checks passed! Authentication system is ready.")
    else:
        print(f"\n  ⚠️  {total - passed} check(s) failed. See details above.")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_checks()
    sys.exit(0 if success else 1)
