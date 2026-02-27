import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
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


@cache_page(60 * 60 * 6)  # Cache for 6 hours (21600 seconds) - less frequent than per-business sitemaps
def sitemap_index(request):
    """
    Generate sitemap index for all published business sitemaps.
    
    ✅ Dynamic: Queries database for all active businesses
    ✅ Cached: 6-hour cache prevents hammering DB (business list changes less frequently)
    ✅ Instant: Subsequent requests served from cache
    ✅ SEO: Google crawls this once, then individual sitemaps via <loc> refs
    
    Returns: sitemap_index.xml with references to all business sitemaps
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch all ACTIVE published businesses with domains
        # Filter: status='active' → ensures only live shops are indexed
        biz_response = supabase.table('business_profiles')\
            .select('id,domain,updated_at,status')\
            .eq('status', 'active')\
            .order('updated_at', desc=True)\
            .limit(50000)\
            .execute()
        
        sitemaps = []
        latest_update = datetime.now()
        
        for biz in biz_response.data:
            domain = biz.get('domain')
            if not domain:
                continue
            
            # Track latest update for Last-Modified header
            biz_updated = biz.get('updated_at')
            if biz_updated:
                try:
                    if isinstance(biz_updated, str):
                        biz_dt = datetime.fromisoformat(biz_updated.replace('Z', '+00:00'))
                    else:
                        biz_dt = biz_updated
                    if biz_dt > latest_update:
                        latest_update = biz_dt
                except:
                    pass
            
            sitemaps.append({
                'loc': f"https://{domain}.nexassearch.com/sitemap.xml",
                'lastmod': format_date(biz_updated),
            })
        
        logger.info(f"Sitemap index includes {len(sitemaps)} business sitemaps")
        
        sitemap_index_xml = render_to_string('storefront/sitemap_index.xml', {
            'sitemaps': sitemaps,
            'now': datetime.now(),
        })
        
        response = HttpResponse(sitemap_index_xml, content_type='application/xml; charset=utf-8')
        
        # Smart caching: 6-hour browser cache + 1-day CDN cache
        response['Cache-Control'] = 'public, max-age=21600, s-maxage=86400, must-revalidate'
        response['Expires'] = '21600'  # Backwards compat for HTTP/1.0
        
        # Set Last-Modified for efficient crawling (304 Not Modified)
        if latest_update:
            response['Last-Modified'] = latest_update.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        return response
        
    except Exception as e:
        logger.exception(f"Sitemap index generation error: {e}")
        return HttpResponse(f"Error generating sitemap index: {str(e)}", status=500)
