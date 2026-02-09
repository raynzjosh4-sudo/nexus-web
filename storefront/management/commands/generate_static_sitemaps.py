import os
import logging
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse
from storefront.client import get_supabase_client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate static XML sitemap files for all published businesses (production-grade)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='storefront/static/sitemaps',
            help='Directory to save sitemap files',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        verbose = options['verbose']
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS('🚀 Starting static sitemap generation...'))
        self.stdout.write(f'Output directory: {output_dir}\n')
        
        try:
            supabase = get_supabase_client()
            
            # Step 1: Fetch all published businesses
            self.stdout.write('📦 Fetching published businesses...')
            biz_response = supabase.table('business_profiles')\
                .select('id,domain,business_name,created_at,logo_url')\
                .eq('status', 'published')\
                .order('created_at', desc=True)\
                .limit(50000)\
                .execute()
            
            businesses = biz_response.data
            business_count = len(businesses)
            
            if business_count == 0:
                self.stdout.write(self.style.WARNING('⚠️ No published businesses found!'))
                return
            
            self.stdout.write(f'✅ Found {business_count} published businesses')
            
            # Step 2: Generate master sitemap index
            self.stdout.write('\n📋 Generating master sitemap index...')
            self._generate_sitemap_index(supabase, businesses, output_dir, verbose)
            self.stdout.write(f'✅ Saved: {output_dir}/sitemap_index.xml')
            
            # Step 3: Generate individual business sitemaps
            self.stdout.write(f'\n🏪 Generating {business_count} business sitemaps...')
            success_count = 0
            error_count = 0
            
            for idx, business in enumerate(businesses, 1):
                try:
                    self._generate_business_sitemap(
                        supabase, business, output_dir, verbose
                    )
                    success_count += 1
                    
                    # Show progress every 100 businesses
                    if idx % 100 == 0:
                        self.stdout.write(f'  Progress: {idx}/{business_count} ✓')
                
                except Exception as e:
                    error_count += 1
                    logger.error(
                        f'Error generating sitemap for {business["domain"]}: {str(e)}'
                    )
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ {business["domain"]}: {str(e)}')
                        )
            
            # Step 4: Generate summary report
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('✅ SITEMAP GENERATION COMPLETE'))
            self.stdout.write('='*60)
            self.stdout.write(f'Businesses processed: {business_count}')
            self.stdout.write(f'  ✅ Successful: {success_count}')
            self.stdout.write(f'  ❌ Failed: {error_count}')
            self.stdout.write(f'\nSitemaps location: {output_dir}')
            self.stdout.write(f'Master index: {output_dir}/sitemap_index.xml')
            self.stdout.write(f'\nNext step: Deploy to production server')
            self.stdout.write(f'Command: cp {output_dir}/* /path/to/static/sitemaps/')
            self.stdout.write('='*60 + '\n')
            
            # Save metadata
            self._save_metadata(output_dir, business_count, success_count, error_count)
            self.stdout.write('📊 Metadata saved to sitemaps_metadata.json')
            
        except Exception as e:
            logger.error(f'Fatal error in sitemap generation: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'\n❌ FATAL ERROR: {str(e)}')
            )
            raise

    def _generate_sitemap_index(self, supabase, businesses, output_dir, verbose):
        """Generate master sitemap_index.xml listing all businesses."""
        try:
            sitemaps = []
            # Use the origin per-subdomain sitemap URL (dynamic endpoint) as the primary
            # reference so newly-created businesses are discoverable immediately.
            for business in businesses:
                domain = business.get('domain')
                sitemaps.append({
                    'loc': f"https://{domain}.nexassearch.com/sitemap.xml",
                    'lastmod': business['created_at'][:10] if business.get('created_at') else datetime.now().isoformat()[:10],
                })
            
            xml = render_to_string('storefront/sitemaps/sitemap_index.xml', {
                'sitemaps': sitemaps,
                'now': datetime.now().isoformat()[:10]
            })
            
            filepath = os.path.join(output_dir, 'sitemap_index.xml')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(xml)
            
            if verbose:
                self.stdout.write(f'  ✓ Master index with {len(sitemaps)} sitemaps')
        
        except Exception as e:
            logger.error(f'Error generating sitemap index: {str(e)}')
            raise

    def _generate_business_sitemap(self, supabase, business, output_dir, verbose):
        """Generate sitemap.xml for a single business with all its products."""
        try:
            business_id = business['id']
            domain = business['domain']
            
            # Fetch all products for this business
            # Try with created_at first (safer fallback)
            posts_response = supabase.table('posts')\
                .select('id,data,created_at')\
                .eq('business_id', business_id)\
                .order('created_at', desc=True)\
                .limit(50000)\
                .execute()
            
            posts = posts_response.data
            
            # Build URL list
            urls = [
                {
                    'loc': f"https://{domain}.nexassearch.com/",
                    'lastmod': business['created_at'][:10] if business.get('created_at') else datetime.now().isoformat()[:10],
                    'changefreq': 'weekly',
                    'priority': '0.8',
                    'images': []
                }
            ]
            
            # Add each product
            for post in posts:
                post_data = post.get('data', {})
                if isinstance(post_data, str):
                    post_data = json.loads(post_data)
                
                # Extract images
                images = []
                if 'images' in post_data and isinstance(post_data['images'], list):
                    for img in post_data['images'][:3]:  # Max 3 images per product
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
                
                url_entry = {
                    'loc': f"https://{domain}.nexassearch.com/product/{post['id']}/",
                    'lastmod': post.get('created_at', business['created_at'])[:10],
                    'changefreq': 'weekly',
                    'priority': '0.7',
                    'images': images
                }
                urls.append(url_entry)
            
            # Render sitemap XML
            xml = render_to_string('storefront/sitemaps/sitemap.xml', {
                'urls': urls
            })
            
            # Save to file
            filename = f"{domain}_sitemap.xml"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(xml)
            
            if verbose:
                self.stdout.write(
                    f'  ✓ {domain}: {len(urls)} URLs ({len(posts)} products)'
                )
        
        except Exception as e:
            logger.error(f'Error generating sitemap for {business["domain"]}: {str(e)}')
            raise

    def _save_metadata(self, output_dir, business_count, success_count, error_count):
        """Save generation metadata for monitoring."""
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
