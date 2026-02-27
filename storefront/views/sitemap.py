import json
import logging
import hashlib
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.views.decorators.http import condition
from ..client import get_supabase_client
from datetime import datetime

logger = logging.getLogger(__name__)


def format_date(date_str):
    """Format date to YYYY-MM-DD (Google sitemap standard)."""
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')
    try:
        if isinstance(date_str, str):
            return date_str[:10]
        return date_str.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')


def _generate_sitemap_for_business(request, subdomain):
    """
    Internal helper: Generate sitemap XML for a specific business.
    Returns tuple: (xml_content, last_modified_timestamp)
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch business
        biz_response = supabase.table('business_profiles')\
            .select('*')\
            .eq('domain', subdomain)\
            .execute()
        
        if not biz_response.data:
            return None, None
        
        business = biz_response.data[0]
        business_id = business.get('id')
        
        # Fetch all products (optimized: only select needed fields)
        posts_response = supabase.table('posts')\
            .select('id,data,updated_at,created_at')\
            .eq('business_id', business_id)\
            .order('updated_at', desc=True)\
            .limit(50000)\
            .execute()
        
        urls = []
        
        # Add shop homepage (highest priority)
        urls.append({
            'loc': request.build_absolute_uri('/'),
            'lastmod': format_date(None),
            'changefreq': 'weekly',
            'priority': '1.0',
            'images': [],
        })
        
        # Add products with images
        latest_update = datetime.now()
        for post in posts_response.data:
            post_data = post.get('data', {})
            product_url = request.build_absolute_uri(f'/product/{post["id"]}/')
            
            # Track latest update for Last-Modified header
            post_updated = post.get('updated_at') or post.get('created_at')
            if post_updated:
                try:
                    if isinstance(post_updated, str):
                        post_dt = datetime.fromisoformat(post_updated.replace('Z', '+00:00'))
                    else:
                        post_dt = post_updated
                    if post_dt > latest_update:
                        latest_update = post_dt
                except:
                    pass
            
            # Extract images for sitemap (max 3 per product)
            images = []
            images_list = post_data.get('images', [])
            if images_list and isinstance(images_list, list):
                for idx, img in enumerate(images_list[:3]):
                    img_url = img.get('url') if isinstance(img, dict) else str(img)
                    if img_url and isinstance(img_url, str) and img_url.startswith('http'):
                        images.append({
                            'loc': img_url,
                            'title': f"{post_data.get('productName', 'Product')} - Image {idx+1}",
                        })
            
            urls.append({
                'loc': product_url,
                'lastmod': format_date(post_updated),
                'changefreq': 'weekly',
                'priority': '0.8',
                'images': images,
            })
        
        sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
        return sitemap_xml, latest_update
        
    except Exception as e:
        logger.exception(f"Sitemap generation error for {subdomain}: {e}")
        return None, None


@cache_page(60 * 60)  # Cache for 1 hour (3600 seconds)
def sitemap_products(request):
    """
    Generate sitemap for products with image references (per-subdomain).
    
    ✅ Dynamic: Queries database on first request
    ✅ Cached: 1-hour cache prevents hammering DB
    ✅ Instant: Subsequent requests served from cache
    ✅ SEO: Last-Modified header helps Google optimize crawl
    
    If no subdomain → redirect to sitemap_index.xml
    """
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        return HttpResponsePermanentRedirect('/sitemap_index.xml')
    
    sitemap_xml, last_modified = _generate_sitemap_for_business(request, subdomain)
    
    if not sitemap_xml:
        return HttpResponse("Business not found", status=404)
    
    response = HttpResponse(
        sitemap_xml,
        content_type='application/xml; charset=utf-8'
    )
    
    # Smart caching headers: 1-hour browser cache + 1-day CDN cache
    response['Cache-Control'] = 'public, max-age=3600, s-maxage=86400, must-revalidate'
    response['Expires'] = '3600'  # Backwards compat for HTTP/1.0
    
    # Set Last-Modified for efficient crawling (304 Not Modified)
    if last_modified:
        response['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return response


@cache_page(60 * 60 * 6)  # Cache for 6 hours (21600 seconds) - business list changes less frequently
def sitemap_businesses(request):
    """Generate sitemap index for all active businesses (use with main domain only)."""
    supabase = get_supabase_client()
    
    # Fetch all published businesses (only select business domain, id exists)
    biz_response = supabase.table('business_profiles').select('id,domain').eq('status', 'active').limit(50000).execute()
    
    urls = []
    for biz in biz_response.data:
        if biz.get('domain'):
            urls.append({
                'loc': f"https://{biz['domain']}.nexassearch.com/",
                'lastmod': format_date(None),  # Use today's date
                'changefreq': 'weekly',
                'priority': '0.9',
            
            })
    
    sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
    return HttpResponse(
        sitemap_xml,
        content_type='application/xml; charset=utf-8',
        headers={'Cache-Control': 'public, max-age=21600, must-revalidate'}
    )
