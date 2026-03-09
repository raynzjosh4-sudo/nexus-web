from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
import logging
import traceback

logger = logging.getLogger(__name__)

class SubdomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().lower()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("Full host is: %s", host)

        # Remove port from host if present
        host_without_port = host.split(':')[0]
        logger.debug("Host without port: %s", host_without_port)
        
        domain_parts = host_without_port.split('.')
        logger.debug("Domain parts: %s", domain_parts)

        # Logic to extract subdomain
        subdomain = None

        from django.conf import settings

        if 'localhost' in host_without_port:
            # Localhost Logic (e.g. test.localhost)
            # Only treat subdomains on localhost if enabled in settings
            if getattr(settings, 'ALLOW_LOCALHOST_SUBDOMAINS', True):
                if len(domain_parts) >= 2 and domain_parts[-1] == 'localhost':
                    subdomain = domain_parts[0]
                    logger.debug("Detected localhost subdomain: %s", subdomain)
            else:
                logger.debug("Localhost subdomain detection disabled by settings.ALLOW_LOCALHOST_SUBDOMAINS")
        else:
            # Production Logic (e.g. mikes-shoes.nexassearch.com)
            # Subdomains are anything before the main domain
            if len(domain_parts) > 2:
                subdomain = domain_parts[0]
                logger.debug("Detected production subdomain: %s", subdomain)

        if subdomain and subdomain != 'www':
            logger.debug("Setting subdomain: %s and urlconf to storefront.urls", subdomain)
            request.subdomain = subdomain
            request.urlconf = 'storefront.urls'
        else:
            logger.debug("No subdomain detected, using main site.")
            request.subdomain = None


class ExceptionMiddleware(MiddlewareMixin):
    """Captures exceptions and logs them for debugging"""
    
    def process_exception(self, request, exception):
        if exception:
            error_details = f"{type(exception).__name__}: {str(exception)}"
            full_traceback = traceback.format_exc()
            
            # Check if this is an expected Http404 for invalid subdomain
            is_expected_404 = (
                isinstance(exception, Http404) and 
                hasattr(request, 'subdomain') and 
                request.subdomain and 
                "not found" in str(exception).lower()
            )
            
            if is_expected_404:
                # Log invalid subdomain access as INFO, not ERROR
                logger.info(f"Invalid subdomain access: {error_details}")
                logger.debug(f"Request details: {request.method} {request.path} from {request.get_host()}")
            else:
                # Log real errors as ERROR
                logger.error(f"Exception caught: {error_details}")
                logger.error(f"Full traceback:\n{full_traceback}")
                logger.error(f"Request: {request.method} {request.path}")
                logger.error(f"User: {request.session.get('user_id', 'Anonymous')}")
            
            # Store exception details for display in error template (only for real errors)
            if not is_expected_404:
                request.exception_details = {
                    'error': error_details,
                    'traceback': full_traceback
                }
        
        return None  # Let Django's error handling take over