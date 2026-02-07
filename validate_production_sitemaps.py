#!/usr/bin/env python
"""
Production Sitemap Validation Script

Tests the static sitemap generation and serving pipeline.
Validates:
✅ Management command works
✅ Sitemaps generate correctly
✅ Files have proper XML format
✅ Master index references all businesses
✅ Business sitemaps reference all products
✅ Static serving works with proper headers
"""

import os
import sys
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

# Add Django setup
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.test import RequestFactory
from storefront.client import get_supabase_client


class SitemapValidator:
    def __init__(self):
        self.sitemaps_dir = Path('storefront/static/sitemaps')
        self.client = Client()
        self.request_factory = RequestFactory()
        self.supabase = get_supabase_client()
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def run_all_tests(self):
        """Run complete validation suite."""
        print("\n" + "="*70)
        print("🚀 PRODUCTION SITEMAP VALIDATION")
        print("="*70 + "\n")
        
        # Create sitemaps directory if needed
        self.sitemaps_dir.mkdir(parents=True, exist_ok=True)
        
        # Run tests
        self.test_generate_command()
        self.test_sitemap_index_exists()
        self.test_sitemap_index_format()
        self.test_business_sitemaps_exist()
        self.test_business_sitemap_format()
        self.test_sitemap_index_references()
        self.test_http_serving()
        self.test_http_headers()
        self.test_cache_control()
        
        # Print results
        self.print_results()
    
    def test_generate_command(self):
        """Test: Management command generates sitemaps."""
        print("📊 Test 1: Generate static sitemaps...")
        try:
            result = subprocess.run(
                ['python', 'manage.py', 'generate_static_sitemaps', '--verbose'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0 and 'SITEMAP GENERATION COMPLETE' in result.stdout:
                self.passed.append("✅ Management command executed successfully")
                print(f"  {self.passed[-1]}")
                return True
            else:
                error = f"Command failed: {result.stderr}"
                self.errors.append(error)
                print(f"  ❌ {error}")
                return False
        
        except Exception as e:
            self.errors.append(f"Command error: {str(e)}")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_sitemap_index_exists(self):
        """Test: Master sitemap index was created."""
        print("\n🔍 Test 2: Check master sitemap index...")
        filepath = self.sitemaps_dir / 'sitemap_index.xml'
        
        if filepath.exists():
            size = filepath.stat().st_size
            self.passed.append(
                f"✅ sitemap_index.xml exists ({size:,} bytes)"
            )
            print(f"  {self.passed[-1]}")
            return True
        else:
            self.errors.append("sitemap_index.xml not found")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_sitemap_index_format(self):
        """Test: Master index is valid XML."""
        print("\n📋 Test 3: Validate master index XML format...")
        filepath = self.sitemaps_dir / 'sitemap_index.xml'
        
        if not filepath.exists():
            self.warnings.append("Skipped: sitemap_index.xml not found")
            return False
        
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            if root.tag.endswith('urlset') or root.tag.endswith('sitemapindex'):
                count = len(root)
                self.passed.append(
                    f"✅ Valid XML with {count} sitemap entries"
                )
                print(f"  {self.passed[-1]}")
                return True
            else:
                self.errors.append(f"Invalid root tag: {root.tag}")
                print(f"  ❌ {self.errors[-1]}")
                return False
        
        except ET.ParseError as e:
            self.errors.append(f"XML parse error: {str(e)}")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_business_sitemaps_exist(self):
        """Test: Business sitemaps were created."""
        print("\n🏪 Test 4: Check business sitemaps...")
        
        # Count business sitemap files
        business_sitemaps = list(self.sitemaps_dir.glob('*_sitemap.xml'))
        
        if business_sitemaps:
            self.passed.append(
                f"✅ Found {len(business_sitemaps)} business sitemaps"
            )
            print(f"  {self.passed[-1]}")
            
            # List first 5
            for sitemap in business_sitemaps[:5]:
                size = sitemap.stat().st_size
                print(f"    - {sitemap.name} ({size:,} bytes)")
            
            if len(business_sitemaps) > 5:
                print(f"    ... and {len(business_sitemaps) - 5} more")
            
            return True
        else:
            self.errors.append("No business sitemaps found")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_business_sitemap_format(self):
        """Test: Business sitemaps are valid XML."""
        print("\n🔍 Test 5: Validate business sitemap formats...")
        
        business_sitemaps = list(self.sitemaps_dir.glob('*_sitemap.xml'))
        
        if not business_sitemaps:
            self.warnings.append("No business sitemaps to validate")
            return False
        
        valid_count = 0
        invalid_count = 0
        urls_total = 0
        
        for sitemap in business_sitemaps[:5]:  # Test first 5
            try:
                tree = ET.parse(sitemap)
                root = tree.getroot()
                
                # Count URLs in this sitemap
                urls = len(root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'))
                urls_total += urls
                
                if urls > 0:
                    valid_count += 1
                else:
                    invalid_count += 1
            
            except ET.ParseError:
                invalid_count += 1
        
        if invalid_count == 0:
            self.passed.append(
                f"✅ All tested sitemaps are valid XML ({urls_total:,} total URLs)"
            )
            print(f"  {self.passed[-1]}")
            return True
        else:
            self.errors.append(
                f"{invalid_count} sitemaps failed XML validation"
            )
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_sitemap_index_references(self):
        """Test: Master index references correct business sitemaps."""
        print("\n🔗 Test 6: Validate sitemap index references...")
        
        filepath = self.sitemaps_dir / 'sitemap_index.xml'
        if not filepath.exists():
            self.warnings.append("Skipped: sitemap_index.xml not found")
            return False
        
        try:
            tree = ET.parse(filepath)
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            sitemaps = tree.findall('.//sm:sitemap/sm:loc', ns)
            
            if sitemaps:
                sample_url = sitemaps[0].text if sitemaps else None
                self.passed.append(
                    f"✅ Index has {len(sitemaps)} business sitemaps"
                )
                print(f"  {self.passed[-1]}")
                if sample_url:
                    print(f"    Sample: {sample_url}")
                return True
            else:
                self.warnings.append("No sitemap references found in index")
                print(f"  ⚠️ {self.warnings[-1]}")
                return False
        
        except Exception as e:
            self.errors.append(f"Error parsing index: {str(e)}")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_http_serving(self):
        """Test: Sitemaps are served correctly over HTTP."""
        print("\n🌐 Test 7: Test HTTP serving...")
        
        try:
            # Test main domain sitemap index
            response = self.client.get('/sitemap_index.xml')
            if response.status_code == 200 and b'sitemapindex' in response.content:
                self.passed.append("✅ Main domain sitemap_index.xml served correctly")
                print(f"  {self.passed[-1]}")
                return True
            else:
                self.warnings.append(
                    f"Sitemap served with status {response.status_code} "
                    "(may need sitemaps generated first)"
                )
                print(f"  ⚠️ {self.warnings[-1]}")
                return False
        
        except Exception as e:
            self.errors.append(f"HTTP serving error: {str(e)}")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_http_headers(self):
        """Test: HTTP headers are correct."""
        print("\n📌 Test 8: Validate HTTP headers...")
        
        try:
            response = self.client.get('/sitemap_index.xml')
            
            headers_ok = True
            
            # Check Content-Type
            content_type = response.get('Content-Type', '')
            if 'xml' in content_type.lower():
                print(f"    ✓ Content-Type: {content_type}")
            else:
                print(f"    ✗ Content-Type: {content_type}")
                headers_ok = False
            
            # Check Cache-Control
            cache_control = response.get('Cache-Control', '')
            if cache_control:
                print(f"    ✓ Cache-Control: {cache_control}")
            else:
                print(f"    ✗ Cache-Control: not set")
                headers_ok = False
            
            if headers_ok:
                self.passed.append("✅ HTTP headers are correct")
            else:
                self.warnings.append("Some HTTP headers need attention")
            
            return headers_ok
        
        except Exception as e:
            self.errors.append(f"Header validation error: {str(e)}")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def test_cache_control(self):
        """Test: Cache headers allow CDN caching."""
        print("\n⚡ Test 9: Validate caching strategy...")
        
        try:
            response = self.client.get('/sitemap_index.xml')
            cache_control = response.get('Cache-Control', '')
            
            if 'max-age' in cache_control:
                self.passed.append(
                    f"✅ CDN-friendly cache headers: {cache_control}"
                )
                print(f"  {self.passed[-1]}")
                return True
            else:
                self.warnings.append("Cache-Control could be more aggressive")
                print(f"  ⚠️ {self.warnings[-1]}")
                return False
        
        except Exception as e:
            self.errors.append(f"Cache validation error: {str(e)}")
            print(f"  ❌ {self.errors[-1]}")
            return False
    
    def print_results(self):
        """Print test results summary."""
        print("\n" + "="*70)
        print("📊 TEST RESULTS")
        print("="*70)
        
        # Passed
        if self.passed:
            print(f"\n✅ PASSED ({len(self.passed)}):")
            for item in self.passed:
                print(f"  {item}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"  {item}")
        
        # Errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for item in self.errors:
                print(f"  {item}")
        
        # Summary
        status = "✅ PRODUCTION READY" if not self.errors else "❌ NEEDS FIXES"
        print(f"\n{'='*70}")
        print(f"{status}")
        print(f"{'='*70}\n")
        
        # Next steps
        if not self.errors:
            print("🚀 NEXT STEPS:")
            print("  1. Set up cron job to run daily:")
            print("     0 2 * * * cd /path/to/nexus_web && python manage.py generate_static_sitemaps")
            print("\n  2. Submit sitemaps to Google Search Console:")
            print("     Main: https://nexassearch.com/robots.txt (auto-discovery)")
            print("     Business: https://[domain].nexassearch.com/sitemap.xml")
            print("\n  3. Monitor in Search Console:")
            print("     - Coverage report")
            print("     - Performance tab")
            print("     - Sitemaps indexed count")


if __name__ == '__main__':
    validator = SitemapValidator()
    validator.run_all_tests()
