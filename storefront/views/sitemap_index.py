from django.http import HttpResponse
from django.template.loader import render_to_string
from ..client import get_supabase_client


def sitemap_index(request):
    """Generate a sitemap index for all business sitemaps."""
    supabase = get_supabase_client()
    
    # Fetch all published businesses with domains
    biz_response = supabase.table('business_profiles').select('domain').eq('status', 'published').limit(50000).execute()
    
    sitemaps = []
    for biz in biz_response.data:
        if biz.get('domain'):
            sitemaps.append({
                'loc': f"https://{biz['domain']}.nexassearch.com/sitemap.xml",
            })
    
    sitemap_index_xml = render_to_string('storefront/sitemap_index.xml', {'sitemaps': sitemaps})
    return HttpResponse(sitemap_index_xml, content_type='application/xml')
