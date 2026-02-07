from django.http import HttpResponse


def robots_txt(request):
    """Generate robots.txt with SEO-optimized crawl directives."""
    subdomain = getattr(request, 'subdomain', None)
    
    if subdomain:
        # Business subdomain - allow search engines to crawl products
        robots_content = f"""User-agent: *
Allow: /
Allow: /product/
Allow: /category/
Disallow: /admin/
Disallow: /login/
Disallow: /signup/
Disallow: /logout/
Disallow: /auth/
Disallow: */order/*
Disallow: */checkout/*
Disallow: /.env
Disallow: /media/uploads/temp/*

User-agent: Googlebot
Crawl-delay: 0
Request-rate: 100/1h

User-agent: Bingbot
Crawl-delay: 1
Request-rate: 30/1h

User-agent: *
Crawl-delay: 1

Sitemap: https://{subdomain}.nexassearch.com/sitemap.xml
"""
    else:
        # Main domain - direct search engines to sitemap index
        robots_content = """User-agent: *
Allow: /robots.txt
Allow: /sitemap*
Disallow: /

User-agent: Googlebot
Allow: /
Crawl-delay: 0

Sitemap: https://nexassearch.com/sitemap_index.xml
"""
    
    return HttpResponse(robots_content, content_type='text/plain')
