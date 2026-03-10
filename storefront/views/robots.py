from django.http import HttpResponse


def robots_txt(request):
    """
    Generate robots.txt with SEO-optimized crawl directives.
    
    PRODUCTION: Points to static sitemaps generated daily via cron.
    Static approach prevents database overload from search engine crawlers.
    """
    subdomain = getattr(request, 'subdomain', None)
    
    if subdomain:
        # Business subdomain - Point to sitemap stored in Supabase storage bucket
        # Each business sitemap is uploaded to the `sitemaps` bucket with
        # filename `<domain>_sitemap.xml`. Using direct public URL avoids
        # generating anything on the Django side.
        import os
        SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
        bucket_url = f"{SUPABASE_URL}/storage/v1/object/public/sitemaps/{request.subdomain}_sitemap.xml"
        robots_content = f"""# Nexus Marketplace - Production Sitemaps
# Sitemap hosted in Supabase storage bucket

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

# Sitemap URL
Sitemap: {bucket_url}
"""
    else:
        # Main domain (nexassearch.com) - Point to static master index
        # Master index updated daily, lists all business sitemaps
        import os
        SUPABASE_URL = os.environ["SUPABASE_URL"]
        BUCKET = "sitemaps"
        master_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/master_index.xml"
        robots_content = f"""# Nexus Marketplace - Main Domain
# Static sitemaps generated daily via cron job
# Command: python manage.py generate_sitemaps

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
Sitemap: {master_url}
"""
    
    return HttpResponse(robots_content, content_type='text/plain')
