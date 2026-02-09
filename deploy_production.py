#!/usr/bin/env python3
"""
PRODUCTION DEPLOYMENT SCRIPT - Nexus Marketplace (nexassearch.com)
Automates setup and validation for production launch
Run: python deploy_production.py
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Color codes for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

class ProductionDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.log = []
        self.errors = []
        
    def print_header(self, text):
        print(f"\n{BLUE}{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}{END}\n")
        self.log.append(f"HEADER: {text}")
        
    def print_success(self, text):
        print(f"{GREEN}✓ {text}{END}")
        self.log.append(f"SUCCESS: {text}")
        
    def print_error(self, text):
        print(f"{RED}✗ {text}{END}")
        self.errors.append(text)
        self.log.append(f"ERROR: {text}")
        
    def print_warning(self, text):
        print(f"{YELLOW}⚠ {text}{END}")
        self.log.append(f"WARNING: {text}")
        
    def print_info(self, text):
        print(f"{BLUE}ℹ {text}{END}")
        self.log.append(f"INFO: {text}")
        
    def run_command(self, cmd, description):
        """Run shell command and report result"""
        self.print_info(f"Running: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.print_success(description)
                return True
            else:
                self.print_error(f"{description}: {result.stderr}")
                return False
        except Exception as e:
            self.print_error(f"{description}: {str(e)}")
            return False
            
    # ========================================================================
    # STEP 1: Validate Environment
    # ========================================================================
    
    def validate_environment(self):
        """Check if production environment is ready"""
        self.print_header("STEP 1: Validate Environment")
        
        checks = {
            "Python 3.10+": f"python --version",
            "PostgreSQL installed": "psql --version",
            "Git installed": "git --version",
            "Django installed": "python -m django --version",
        }
        
        passed = 0
        for check_name, cmd in checks.items():
            try:
                subprocess.run(cmd, shell=True, capture_output=True, check=True)
                self.print_success(check_name)
                passed += 1
            except:
                self.print_warning(f"{check_name} not found")
                
        return passed >= 3
        
    # ========================================================================
    # STEP 2: Validate Configuration Files
    # ========================================================================
    
    def validate_config_files(self):
        """Check if all required config files exist"""
        self.print_header("STEP 2: Validate Configuration Files")
        
        required_files = {
            "Django settings": "core/settings.py",
            "URLs configuration": "storefront/urls.py",
            "Supabase client": "storefront/client.py",
            "SEO views": "storefront/views/seo_views.py",
            "Base SEO template": "storefront/templates/storefront/pages/base_seo.html",
            "Community template": "storefront/templates/storefront/pages/community_detail.html",
            "Lost & Found template": "storefront/templates/storefront/pages/lost_found_detail.html",
            "Swap template": "storefront/templates/storefront/pages/swap_detail.html",
            "User profile template": "storefront/templates/storefront/pages/user_profile.html",
            "Business profile template": "storefront/templates/storefront/pages/business_profile.html",
            "Category template": "storefront/templates/storefront/pages/category_list.html",
            "FAQ template": "storefront/templates/storefront/pages/faq.html",
        }
        
        missing = []
        for name, filepath in required_files.items():
            full_path = self.project_root / filepath
            if full_path.exists():
                self.print_success(f"{name}: {filepath}")
            else:
                self.print_error(f"{name}: {filepath} (MISSING)")
                missing.append(filepath)
                
        return len(missing) == 0
        
    # ========================================================================
    # STEP 3: Validate Database
    # ========================================================================
    
    def validate_database(self):
        """Check if database is accessible"""
        self.print_header("STEP 3: Validate Database")
        
        try:
            # Try to connect to Supabase
            from storefront.client import get_supabase_client
            supabase = get_supabase_client()
            
            # Test each table
            tables_to_check = [
                ('community_posts', 'Community Posts'),
                ('lost_found_items', 'Lost & Found Items'),
                ('swap_items', 'Swap Items'),
                ('posts', 'Products'),
                ('business_profiles', 'Business Profiles'),
            ]
            
            for table_name, display_name in tables_to_check:
                try:
                    result = supabase.table(table_name).select('COUNT()').execute()
                    self.print_success(f"{display_name} table accessible")
                except Exception as e:
                    self.print_warning(f"{display_name} table: {str(e)}")
                    
            return True
        except Exception as e:
            self.print_error(f"Database check failed: {str(e)}")
            return False
            
    # ========================================================================
    # STEP 4: Test Django
    # ========================================================================
    
    def test_django(self):
        """Run Django checks and tests"""
        self.print_header("STEP 4: Test Django")
        
        # Run Django checks
        if self.run_command(
            "python manage.py check",
            "Django system checks"
        ):
            self.print_success("Django configuration valid")
        else:
            self.print_error("Django configuration has issues")
            return False
            
        # Collect static files
        if self.run_command(
            "python manage.py collectstatic --noinput",
            "Static files collected"
        ):
            self.print_success("Static files ready")
        else:
            self.print_warning("Static files collection had issues")
            
        return True
        
    # ========================================================================
    # STEP 5: Validate SEO Views
    # ========================================================================
    
    def validate_seo_views(self):
        """Test that SEO views work correctly"""
        self.print_header("STEP 5: Validate SEO Views")
        
        try:
            from storefront.views.seo_views import (
                build_json_ld_schema,
                community_detail_view,
                lost_found_detail_view,
                swap_detail_view,
                user_profile_view,
                business_profile_view,
                category_list_view,
                faq_view
            )
            self.print_success("All SEO view functions imported successfully")
            
            # Test schema builder with dummy data
            test_data = {
                'title': 'Test Community Post',
                'body': 'This is a test',
                'author': 'Test User',
                'created_at': '2024-01-01',
                'image_url': 'https://example.com/image.jpg',
                'category': 'test'
            }
            
            schema = build_json_ld_schema('community_post', test_data)
            if schema.get('@type') == 'DiscussionForumPosting':
                self.print_success("JSON-LD schema builder working correctly")
            else:
                self.print_error(f"Schema type incorrect: {schema.get('@type')}")
                
            return True
        except Exception as e:
            self.print_error(f"SEO views validation failed: {str(e)}")
            return False
            
    # ========================================================================
    # STEP 6: Generate Sitemaps
    # ========================================================================
    
    def generate_sitemaps(self):
        """Generate sitemap files for SEO"""
        self.print_header("STEP 6: Generate Sitemaps")
        
        if self.run_command(
            "python run_sitemap_generation.py",
            "Sitemap generation completed"
        ):
            self.print_success("Sitemaps generated successfully")
            return True
        else:
            self.print_warning("Sitemap generation failed, continuing anyway")
            return True  # Don't stop deployment for this
            
    # ========================================================================
    # STEP 7: Production Settings Check
    # ========================================================================
    
    def check_production_settings(self):
        """Validate production-specific settings"""
        self.print_header("STEP 7: Production Settings Check")
        
        from django.conf import settings
        
        checks = {
            "DEBUG = False": not settings.DEBUG,
            "SECRET_KEY set": len(settings.SECRET_KEY) > 50,
            "ALLOWED_HOSTS configured": len(settings.ALLOWED_HOSTS) > 0,
            "Database URL set": hasattr(settings, 'DATABASES'),
        }
        
        all_good = True
        for check_name, result in checks.items():
            if result:
                self.print_success(check_name)
            else:
                self.print_error(f"{check_name} - FIX REQUIRED FOR PRODUCTION")
                all_good = False
                
        return all_good
        
    # ========================================================================
    # STEP 8: Security Checks
    # ========================================================================
    
    def security_checks(self):
        """Run security validation checks"""
        self.print_header("STEP 8: Security Checks")
        
        from django.conf import settings
        
        checks = {
            "SECURE_SSL_REDIRECT": getattr(settings, 'SECURE_SSL_REDIRECT', False),
            "SESSION_COOKIE_SECURE": getattr(settings, 'SESSION_COOKIE_SECURE', False),
            "CSRF_COOKIE_SECURE": getattr(settings, 'CSRF_COOKIE_SECURE', False),
            "HTTPS enabled": 'https://' in getattr(settings, 'ALLOWED_HOSTS', [''])[0],
        }
        
        for check_name, result in checks.items():
            if result:
                self.print_success(f"{check_name}: Enabled")
            else:
                self.print_warning(f"{check_name}: Disabled (enable for production)")
                
        return True
        
    # ========================================================================
    # STEP 9: Google OAuth Validation
    # ========================================================================
    
    def validate_google_oauth(self):
        """Check Google OAuth configuration"""
        self.print_header("STEP 9: Google OAuth Validation")
        
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if client_id and '.apps.googleusercontent.com' in client_id:
            self.print_success("Google Client ID configured")
        else:
            self.print_warning("Google Client ID not properly configured")
            self.print_info("Set GOOGLE_CLIENT_ID in .env with format: xxx.apps.googleusercontent.com")
            
        if client_secret:
            self.print_success("Google Client Secret configured")
        else:
            self.print_warning("Google Client Secret not configured")
            self.print_info("Set GOOGLE_CLIENT_SECRET in .env")
            
        return True
        
    # ========================================================================
    # STEP 10: Final Report
    # ========================================================================
    
    def generate_report(self):
        """Generate deployment readiness report"""
        self.print_header("STEP 10: Deployment Readiness Report")
        
        total_errors = len(self.errors)
        
        if total_errors == 0:
            print(f"{GREEN}✓✓✓ YOUR APPLICATION IS READY FOR PRODUCTION ✓✓✓{END}\n")
            self.print_success("All checks passed!")
            return True
        else:
            print(f"{RED}✗ DEPLOYMENT BLOCKED - {total_errors} issue(s) found:{END}\n")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            return False
            
    # ========================================================================
    # Save Deployment Log
    # ========================================================================
    
    def save_log(self):
        """Save deployment report to file"""
        log_file = self.project_root / f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.log))
        self.print_info(f"Deployment log saved: {log_file}")
        
    # ========================================================================
    # Main Deployment Flow
    # ========================================================================
    
    def deploy(self):
        """Run complete deployment validation"""
        print(f"{GREEN}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║   NEXUS MARKETPLACE - PRODUCTION DEPLOYMENT VALIDATOR      ║")
        print("║              Domain: nexassearch.com                       ║")
        print("║            Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "                     ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{END}\n")
        
        # Run all validation steps
        steps = [
            ("Environment", self.validate_environment),
            ("Configuration Files", self.validate_config_files),
            ("Database", self.validate_database),
            ("Django", self.test_django),
            ("SEO Views", self.validate_seo_views),
            ("Sitemaps", self.generate_sitemaps),
            ("Production Settings", self.check_production_settings),
            ("Security", self.security_checks),
            ("Google OAuth", self.validate_google_oauth),
        ]
        
        results = {}
        for step_name, step_func in steps:
            try:
                results[step_name] = step_func()
            except Exception as e:
                self.print_error(f"Step '{step_name}' failed: {str(e)}")
                results[step_name] = False
                
        # Generate final report
        is_ready = self.generate_report()
        
        # Save log
        self.save_log()
        
        return is_ready


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    deployer = ProductionDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)
