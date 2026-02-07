from django.http import HttpResponse


def robots_txt(request):
    """
    Generate robots.txt with SEO-optimized crawl directives.
    
    PRODUCTION: Points to static sitemaps generated daily via cron.
    Static approach prevents database overload from search engine crawlers.
    """
    subdomain = getattr(request, 'subdomain', None)
    
    if subdomain:
        # Business subdomain - Point to static sitemap file
        # Sitemap generated via: python manage.py generate_static_sitemaps
        robots_content = f"""# Nexus Marketplace - Production Sitemaps
# Generated: Daily via cron job
# Command: python manage.py generate_static_sitemaps

User-agent: *
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

# Static sitemap - generated daily, prevents database overload
Sitemap: https://{subdomain}.nexassearch.com/static/sitemaps/{subdomain}_sitemap.xml
"""
    else:
        # Main domain (nexassearch.com) - Point to static master index
        # Master index updated daily, lists all business sitemaps
        robots_content = """# Nexus Marketplace - Main Domain
# Static sitemaps generated daily via cron job
# Command: python manage.py generate_static_sitemaps

User-agent: *
Allow: /robots.txt
Allow: /static/sitemaps/*
Disallow: /

User-agent: Googlebot
Allow: /
Crawl-delay: 0
Request-rate: 100/1h

User-agent: Bingbot
Allow: /static/sitemaps/*
Crawl-delay: 1
Request-rate: 30/1h

User-agent: *
Crawl-delay: 1

# Master sitemap index - lists all business sitemaps (updated daily)
Sitemap: https://nexassearch.com/static/sitemaps/sitemap_index.xml
"""
    
    return HttpResponse(robots_content, content_type='text/plain')
