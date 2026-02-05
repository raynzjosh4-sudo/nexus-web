import json
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from ..client import get_supabase_client
from datetime import datetime
from urllib.parse import urljoin


def sitemap_products(request):
    """Generate sitemap for products indexed by Google."""
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        return HttpResponse("Sitemap not available", status=404)

    supabase = get_supabase_client()
    
    # Fetch business
    biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    if not biz_response.data:
        return HttpResponse("Business not found", status=404)
    
    business_id = biz_response.data[0].get('id')
    
    # Fetch all products
    posts_response = supabase.table('posts').select('id,created_at,updated_at').eq('business_id', business_id).order('updated_at', desc=True).execute()
    
    urls = []
    for post in posts_response.data:
        urls.append({
            'loc': request.build_absolute_uri(f'/product/{post["id"]}/'),
            'lastmod': post.get('updated_at', post.get('created_at', datetime.now().isoformat())),
            'changefreq': 'weekly',
            'priority': '0.8',
        })
    
    # Add shop home
    urls.insert(0, {
        'loc': request.build_absolute_uri('/'),
        'lastmod': datetime.now().isoformat(),
        'changefreq': 'daily',
        'priority': '1.0',
    })
    
    sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
    return HttpResponse(sitemap_xml, content_type='application/xml')


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
                'lastmod': biz.get('updated_at', datetime.now().isoformat()),
                'changefreq': 'weekly',
                'priority': '0.9',
            })
    
    sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
    return HttpResponse(sitemap_xml, content_type='application/xml')
