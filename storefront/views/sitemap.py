"""
Sitemap views for Nexus Web storefront.

Generates XML sitemaps for SEO:
- sitemap.xml: Per-business product sitemap with images
- sitemap_index.xml: Master index of all business sitemaps (main domain only)
"""

import logging
from django.http import HttpResponse
from django.urls import reverse
from ..client import get_supabase_client

logger = logging.getLogger(__name__)


def sitemap_view(request):
    """
    Generate sitemap.xml for the current business subdomain.
    Includes all active products with images.
    """
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        # Main domain - redirect to sitemap_index
        return sitemap_index_view(request)

    try:
        supabase = get_supabase_client()

        # Get business info
        biz_response = supabase.table('business_profiles').select('id, domain, status').eq('domain', subdomain).execute()
        if not biz_response.data:
            return HttpResponse("Business not found", status=404, content_type='text/plain')

        business = biz_response.data[0]
        if business.get('status') != 'active':
            return HttpResponse("Business not active", status=404, content_type='text/plain')

        business_id = business['id']

        # Get all products for this business
        products_response = supabase.table('posts').select('id, data, created_at').eq('business_id', business_id).execute()
        products = products_response.data or []

        # Build XML
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
        xml_parts.append('        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')

        for post in products:
            post_data = post.get('data', {})
            product_name = post_data.get('productName', 'Untitled')
            images = post_data.get('images', [])

            # Product URL
            product_url = f"https://{subdomain}.nexassearch.com/product/{post['id']}/"

            xml_parts.append('  <url>')
            xml_parts.append(f'    <loc>{product_url}</loc>')
            xml_parts.append(f'    <lastmod>{post["created_at"][:10]}</lastmod>')  # YYYY-MM-DD
            xml_parts.append('    <changefreq>weekly</changefreq>')
            xml_parts.append('    <priority>0.8</priority>')

            # Add images
            for img in images:
                if isinstance(img, dict) and 'url' in img:
                    img_url = img['url']
                    xml_parts.append('    <image:image>')
                    xml_parts.append(f'      <image:loc>{img_url}</image:loc>')
                    xml_parts.append(f'      <image:caption>{product_name}</image:caption>')
                    xml_parts.append('    </image:image>')

            xml_parts.append('  </url>')

        xml_parts.append('</urlset>')

        xml_content = '\n'.join(xml_parts)
        return HttpResponse(xml_content, content_type='application/xml')

    except Exception as e:
        logger.error(f"Sitemap generation failed for {subdomain}: {str(e)}")
        return HttpResponse("Sitemap generation failed", status=500, content_type='text/plain')


def sitemap_index_view(request):
    """
    Generate sitemap_index.xml for the main domain.
    Lists all active business sitemaps.
    """
    subdomain = getattr(request, 'subdomain', None)
    if subdomain:
        # Subdomain - redirect to business sitemap
        return sitemap_view(request)

    try:
        supabase = get_supabase_client()

        # Get all active businesses
        biz_response = supabase.table('business_profiles').select('domain').eq('status', 'active').execute()
        businesses = biz_response.data or []

        # Build XML
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for biz in businesses:
            domain = biz['domain']
            sitemap_url = f"https://{domain}.nexassearch.com/sitemap.xml"

            xml_parts.append('  <sitemap>')
            xml_parts.append(f'    <loc>{sitemap_url}</loc>')
            xml_parts.append('    <lastmod>2024-01-01</lastmod>')  # Could be dynamic
            xml_parts.append('  </sitemap>')

        xml_parts.append('</sitemapindex>')

        xml_content = '\n'.join(xml_parts)
        return HttpResponse(xml_content, content_type='application/xml')

    except Exception as e:
        logger.error(f"Sitemap index generation failed: {str(e)}")
        return HttpResponse("Sitemap index generation failed", status=500, content_type='text/plain')