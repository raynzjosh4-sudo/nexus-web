import json
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from ..client import get_supabase_client
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


def format_date(date_str):
    """Format date to YYYY-MM-DD (Google sitemap standard)."""
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')
    try:
        # Handle ISO 8601 timestamps with timezone
        if isinstance(date_str, str):
            # Extract date portion (YYYY-MM-DD)
            return date_str[:10]
        return date_str.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')


def sitemap_products(request):
    """Generate sitemap for products with image references."""
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        return HttpResponse("Sitemap not available", status=404)

    try:
        supabase = get_supabase_client()
        
        # Fetch business
        biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
        if not biz_response.data:
            return HttpResponse("Business not found", status=404)
        
        business_id = biz_response.data[0].get('id')
        
        # Fetch all products
        posts_response = supabase.table('posts')\
            .select('id,data,created_at,updated_at')\
            .eq('business_id', business_id)\
            .order('updated_at', desc=True)\
            .limit(50000)\
            .execute()
        
        urls = []
        
        # Add shop homepage first (highest priority)
        urls.append({
            'loc': request.build_absolute_uri('/'),
            'lastmod': format_date(None),
            'changefreq': 'weekly',
            'priority': '1.0',
            'images': [],
        })
        
        # Add products (check changefreq)
        for post in posts_response.data:
            post_data = post.get('data', {})
            product_url = request.build_absolute_uri(f'/product/{post["id"]}/')
            
            # Extract images for sitemap
            images = []
            images_list = post_data.get('images', [])
            if images_list and isinstance(images_list, list):
                for idx, img in enumerate(images_list[:3]):  # Max 3 images per product
                    img_url = img.get('url') if isinstance(img, dict) else str(img)
                    if img_url and img_url.startswith('http'):
                        images.append({
                            'loc': img_url,
                            'title': f"{post_data.get('productName', 'Product')} - Image {idx+1}",
                        })
            
            # Determine last modified date - properly formatted
            raw_date = post.get('updated_at') or post.get('created_at')
            lastmod = format_date(raw_date)
            
            urls.append({
                'loc': product_url,
                'lastmod': lastmod,
                'changefreq': 'weekly',
                'priority': '0.8',
                'images': images,
            })
        
        sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
        return HttpResponse(sitemap_xml, content_type='application/xml')
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Sitemap generation error: {e}")
        return HttpResponse(f"Error generating sitemap: {str(e)}", status=500)


def sitemap_businesses(request):
    """Generate sitemap for all businesses (use with main domain only)."""
    supabase = get_supabase_client()
    
    # Fetch all published businesses
    biz_response = supabase.table('business_profiles').select('id,domain,updated_at').eq('status', 'published').limit(50000).execute()
    
    urls = []
    for biz in biz_response.data:
        if biz.get('domain'):
            urls.append({
                'loc': f"https://{biz['domain']}.nexassearch.com/",
                'lastmod': format_date(biz.get('updated_at')),
                'changefreq': 'weekly',
                'priority': '0.9',
            
            })
    
    sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
    return HttpResponse(sitemap_xml, content_type='application/xml')
