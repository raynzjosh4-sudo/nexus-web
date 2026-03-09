import os
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.core.management import call_command

logger = logging.getLogger(__name__)


@csrf_exempt
def trigger_sitemap_job(request):
    """
    Secure webhook endpoint to trigger sitemap generation.
    
    Only accepts POST requests with valid X-Secret header.
    Triggers the generate_sitemaps management command.
    
    Usage:
        POST /run-sitemap-update/
        Header: X-Secret: <SITEMAP_CRON_SECRET>
    
    Returns:
        200 OK with success message if authenticated and executed
        403 Forbidden if wrong method or invalid/missing secret
    """
    SECRET = os.environ.get('SITEMAP_CRON_SECRET', 'missing')
    
    # Only allow POST requests
    if request.method != 'POST':
        logger.warning(f"Sitemap webhook received {request.method} request (expected POST)")
        return HttpResponseForbidden('POST required')
    
    # Check the secret token
    provided_secret = request.headers.get('X-Secret', '')
    if provided_secret != SECRET:
        logger.warning(f"Sitemap webhook received invalid secret token")
        return HttpResponseForbidden('Forbidden')
    
    try:
        # Trigger the sitemap generation command
        logger.info("Executing sitemap generation via webhook")
        call_command('generate_sitemaps')
        logger.info("Sitemap generation completed successfully")
        return JsonResponse({'status': 'success', 'message': 'Sitemap updated!'}, status=200)
    except Exception as e:
        logger.error(f"Error generating sitemaps: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
