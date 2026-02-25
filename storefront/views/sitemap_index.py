import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from ..client import get_supabase_client
from datetime import datetime


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


def sitemap_index(request):
    """Generate sitemap index for all published business sitemaps."""
    try:
        supabase = get_supabase_client()
        
        # Fetch all published businesses with domains
        biz_response = supabase.table('business_profiles')\
            .select('domain,updated_at')\
            .eq('status', 'active')\
            .limit(50000)\
            .execute()
        
        sitemaps = []
        for biz in biz_response.data:
            if biz.get('domain'):
                sitemaps.append({
                    'loc': f"https://{biz['domain']}.nexassearch.com/sitemap.xml",
                    'lastmod': format_date(biz.get('updated_at')),
                })
        
        logger.info(f"Sitemap index includes {len(sitemaps)} business sitemaps")
        sitemap_index_xml = render_to_string('storefront/sitemap_index.xml', {
            'sitemaps': sitemaps,
            'now': datetime.now(),
        })
        return HttpResponse(sitemap_index_xml, content_type='application/xml')
        
    except Exception as e:
        logger.exception(f"Sitemap index generation error: {e}")
        return HttpResponse(f"Error generating sitemap index: {str(e)}", status=500)
