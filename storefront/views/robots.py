from django.http import HttpResponse


def robots_txt(request):
    """Generate robots.txt with sitemap reference."""
    subdomain = getattr(request, 'subdomain', None)
    
    if subdomain:
        # Business subdomain
        robots_content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /login/
Disallow: /signup/
Disallow: /logout/
Disallow: */order/
Crawl-delay: 1
Sitemap: https://{subdomain}.nexassearch.com/sitemap.xml
"""
    else:
        # Main domain
        robots_content = """User-agent: *
Allow: /
Crawl-delay: 1
Sitemap: https://nexassearch.com/sitemap_index.xml
"""
    
    return HttpResponse(robots_content, content_type='text/plain')
