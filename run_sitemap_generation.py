#!/usr/bin/env python
"""
Wrapper script to fix database schema and run sitemap generation
"""
import os
import sys

# Add to Python path (Windows compatible)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.chdir(script_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

# Now run the command with patched status
import logging
import json
from datetime import datetime
from django.template.loader import render_to_string
from storefront.client import get_supabase_client

logger = logging.getLogger(__name__)

def generate_sitemaps():
    """Generate static sitemaps for all ACTIVE businesses"""
    
    output_dir = 'storefront/static/sitemaps'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("🚀 PRODUCTION SITEMAP GENERATION")
    print("="*70 + "\n")
    
    try:
        supabase = get_supabase_client()
        
        # Fetch all ACTIVE businesses (not 'published')
        print("📦 Fetching active businesses from database...")
        biz_response = supabase.table('business_profiles')\
            .select('id,domain,business_name,created_at,logo_url')\
            .eq('status', 'active')\
            .order('created_at', desc=True)\
            .limit(50000)\
            .execute()
        
        businesses = biz_response.data
        business_count = len(businesses)
        
        if business_count == 0:
            print("⚠️ No active businesses found!")
            return False
        
        print(f"✅ Found {business_count} active businesses\n")
        
        # Generate master index
        print("📋 Generating master sitemap index...")
        sitemaps = []
        # Use the static CDN host for sitemap files so search engines can fetch them
        static_host = os.getenv('STATIC_SITEMAP_HOST', 'https://static.nexassearch.com')
        for business in businesses:
            sitemaps.append({
                'loc': f"{static_host}/static/sitemaps/{business['domain']}_sitemap.xml",
                'lastmod': business['created_at'][:10] if business.get('created_at') else datetime.now().isoformat()[:10],
            })
        
        xml = render_to_string('storefront/sitemap_index.xml', {
            'sitemaps': sitemaps,
            'now': datetime.now().isoformat()[:10]
        })
        
        with open(os.path.join(output_dir, 'sitemap_index.xml'), 'w', encoding='utf-8') as f:
            f.write(xml)
        
        print(f"✅ Generated master index with {len(sitemaps)} business sitemaps\n")
        
        # Generate individual business sitemaps
        print(f"🏪 Generating {business_count} business sitemaps...")
        success_count = 0
        error_count = 0
        
        for idx, business in enumerate(businesses, 1):
            try:
                business_id = business['id']
                domain = business['domain']
                
                # Fetch all products
                posts_response = supabase.table('posts')\
                    .select('id,data,created_at')\
                    .eq('business_id', business_id)\
                    .order('created_at', desc=True)\
                    .limit(50000)\
                    .execute()
                
                posts = posts_response.data
                
                # Build URLs
                urls = [{
                    'loc': f"https://{domain}.nexassearch.com/",
                    'lastmod': business['created_at'][:10] if business.get('created_at') else datetime.now().isoformat()[:10],
                    'changefreq': 'weekly',
                    'priority': '0.8',
                    'images': []
                }]
                
                # Add products
                for post in posts:
                    post_data = post.get('data', {})
                    if isinstance(post_data, str):
                        post_data = json.loads(post_data)
                    
                    # Extract images
                    images = []
                    if 'images' in post_data and isinstance(post_data['images'], list):
                        for img in post_data['images'][:3]:
                            img_url = None
                            if isinstance(img, dict):
                                img_url = img.get('url')
                            elif isinstance(img, str):
                                img_url = img
                            
                            if img_url and img_url.startswith('http'):
                                images.append({
                                    'loc': img_url,
                                    'title': post_data.get('productName', 'Product Image')
                                })
                    
                    urls.append({
                        'loc': f"https://{domain}.nexassearch.com/product/{post['id']}/",
                        'lastmod': post.get('created_at', business['created_at'])[:10],
                        'changefreq': 'weekly',
                        'priority': '0.7',
                        'images': images
                    })
                
                # Render and save
                xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
                filepath = os.path.join(output_dir, f"{domain}_sitemap.xml")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(xml)
                
                success_count += 1
                
                # Progress
                if idx % 5 == 0 or idx == business_count:
                    print(f"  Progress: {idx}/{business_count} ✓ ({success_count} generated)")
            
            except Exception as e:
                error_count += 1
                print(f"  ❌ Error for {business['domain']}: {str(e)}")
        
        # Summary
        print("\n" + "="*70)
        print("✅ SITEMAP GENERATION COMPLETE")
        print("="*70)
        print(f"Businesses processed: {business_count}")
        print(f"  ✅ Successful: {success_count}")
        print(f"  ❌ Failed: {error_count}")
        print(f"\nSitemaps saved to: {output_dir}/")
        print("\nGenerated files:")
        print(f"  - sitemap_index.xml (master index)")
        for business in businesses[:5]:
            domain = business['domain']
            filepath = os.path.join(output_dir, f"{domain}_sitemap.xml")
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  - {domain}_sitemap.xml ({size:,} bytes)")
        if business_count > 5:
            print(f"  ... and {business_count - 5} more")
        
        print("\n📊 Metadata saved")
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'total_businesses': business_count,
            'successful': success_count,
            'failed': error_count,
            'status': 'success' if error_count == 0 else 'partial'
        }
        
        metadata_path = os.path.join(output_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("="*70 + "\n")
        
        return error_count == 0
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    success = generate_sitemaps()
    sys.exit(0 if success else 1)
