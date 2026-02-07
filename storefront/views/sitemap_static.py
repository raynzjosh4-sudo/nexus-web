"""
Static Sitemap Server - Production Grade

Serves pre-generated static sitemap files with proper HTTP headers.
Sitemaps are generated daily via: python manage.py generate_static_sitemaps

This approach:
✅ Zero database queries (prevents overload from Google crawl)
✅ Instant response (no rendering overhead)
✅ Proper HTTP caching (304 Not Modified)
✅ Scales to millions of URLs
✅ Works with CDNs and caching layers
"""

import os
import logging
from django.http import HttpResponse, Http404
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_page
from django.conf import settings

logger = logging.getLogger(__name__)


def get_sitemap_file(subdomain=None):
    """Get the path to the sitemap file."""
    sitemaps_dir = os.path.join(settings.BASE_DIR, 'storefront', 'static', 'sitemaps')
    
    if subdomain:
        # Business subdomain: {subdomain}_sitemap.xml
        filename = f"{subdomain}_sitemap.xml"
    else:
        # Main domain: sitemap_index.xml
        filename = "sitemap_index.xml"
    
    filepath = os.path.join(sitemaps_dir, filename)
    
    # Security: prevent directory traversal
    if not os.path.abspath(filepath).startswith(os.path.abspath(sitemaps_dir)):
        return None
    
    return filepath if os.path.exists(filepath) else None


def sitemap_last_modified(request, subdomain=None):
    """Return the last modified time of the sitemap file."""
    filepath = get_sitemap_file(subdomain)
    
    if not filepath:
        return None
    
    try:
        return os.path.getmtime(filepath)
    except (OSError, IOError):
        return None


@condition(last_modified_func=lambda r, s: sitemap_last_modified(r, s))
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def sitemap_products(request, subdomain=None):
    """
    Serve static sitemap.xml for business subdomain.
    
    Call: GET /sitemap.xml (when on subdomain like alice.nexassearch.com)
    Returns: Pre-generated XML file
    
    Performance:
    - No database queries
    - Served with HTTP 304 caching
    - 24-hour browser cache
    - CDN-friendly
    """
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        # Main domain should return 404
        raise Http404("Sitemap not found. Use /static/sitemaps/sitemap_index.xml")
    
    filepath = get_sitemap_file(subdomain)
    
    if not filepath:
        logger.warning(f'Sitemap not found for domain: {subdomain}')
        raise Http404(
            f"Sitemap for {subdomain} not generated yet. "
            "Run: python manage.py generate_static_sitemaps"
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return HttpResponse(
            content,
            content_type='application/xml',
            headers={
                'Cache-Control': 'public, max-age=86400',  # 24 hours
                'X-Sitemap-Generated': 'static',
            }
        )
    
    except IOError as e:
        logger.error(f'Error reading sitemap {filepath}: {str(e)}')
        raise Http404(f"Error reading sitemap: {str(e)}")


@condition(last_modified_func=sitemap_last_modified)
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def sitemap_index(request):
    """
    Serve static sitemap_index.xml from main domain.
    
    Call: GET /sitemap_index.xml (from main domain like nexassearch.com)
    Returns: Master sitemap index listing all business sitemaps
    
    Performance:
    - No database queries
    - Served with HTTP 304 caching
    - 24-hour browser cache
    - CDN-friendly
    
    Generation:
    - Updated daily via cron: python manage.py generate_static_sitemaps
    """
    subdomain = getattr(request, 'subdomain', None)
    
    if subdomain:
        # Business subdomain should use business sitemap
        raise Http404(
            f"Use /sitemap.xml for business sitemaps"
        )
    
    filepath = get_sitemap_file(subdomain=None)
    
    if not filepath:
        logger.warning('Master sitemap index not found')
        raise Http404(
            "Sitemap index not generated yet. "
            "Run: python manage.py generate_static_sitemaps"
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return HttpResponse(
            content,
            content_type='application/xml',
            headers={
                'Cache-Control': 'public, max-age=86400',  # 24 hours
                'X-Sitemap-Generated': 'static',
            }
        )
    
    except IOError as e:
        logger.error(f'Error reading sitemap index {filepath}: {str(e)}')
        raise Http404(f"Error reading sitemap index: {str(e)}")


def serve_sitemap_file(request, filename):
    """
    Serve any file from storefront/static/sitemaps/ when requested via
    /static/sitemaps/<filename>. This allows mapping static.nexassearch.com
    to the same Django host and serving sitemaps without touching the
    frontend repo or external storage.
    """
    # Basic filename validation: only allow xml and json files, no traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise Http404('Invalid filename')

    allowed_ext = ('.xml', '.json')
    if not filename.lower().endswith(allowed_ext):
        raise Http404('Unsupported file type')

    sitemaps_dir = os.path.join(settings.BASE_DIR, 'storefront', 'static', 'sitemaps')
    filepath = os.path.join(sitemaps_dir, filename)

    if not os.path.exists(filepath):
        raise Http404('Sitemap not found')

    try:
        with open(filepath, 'rb') as f:
            data = f.read()

        content_type = 'application/xml' if filename.lower().endswith('.xml') else 'application/json'
        return HttpResponse(
            data,
            content_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=86400',
                'X-Sitemap-Generated': 'static-file',
            }
        )

    except IOError as e:
        logger.error(f'Error reading sitemap file {filepath}: {str(e)}')
        raise Http404('Error reading sitemap file')
