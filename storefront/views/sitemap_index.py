import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from ..client import get_supabase_client
from datetime import datetime


logger = logging.getLogger(__name__)


def sitemap_index(request):
    """Generate sitemap index for all published business sitemaps."""
    try:
        supabase = get_supabase_client()
        
        # Fetch all published businesses with domains
        biz_response = supabase.table('business_profiles')\
            .select('domain,updated_at')\
            .eq('status', 'published')\
            .limit(50000)\
            .execute()
        
        sitemaps = []
        for biz in biz_response.data:
            if biz.get('domain'):
                sitemaps.append({
                    'loc': f"https://{biz['domain']}.nexassearch.com/sitemap.xml",
                    'lastmod': biz.get('updated_at', datetime.now().isoformat()),
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
