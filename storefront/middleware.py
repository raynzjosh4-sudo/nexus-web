from django.utils.deprecation import MiddlewareMixin

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

        if 'localhost' in host_without_port:
            # Localhost Logic (e.g. test.localhost)
            # For localhost, anything before 'localhost' is the subdomain
            if len(domain_parts) >= 2 and domain_parts[-1] == 'localhost':
                subdomain = domain_parts[0]
                logger.debug("Detected localhost subdomain: %s", subdomain)
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