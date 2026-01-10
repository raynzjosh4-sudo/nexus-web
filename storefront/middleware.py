from django.utils.deprecation import MiddlewareMixin

class SubdomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().lower()
        domain_parts = host.split('.')
        
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("Host is %s", host)

        # Logic to extract subdomain
        subdomain = None

        if 'localhost' in host:
            # Localhost Logic (e.g. test.localhost:8000)
            if len(domain_parts) == 2:
                subdomain = domain_parts[0]
        else:
            # Production Logic (e.g. mikes-shoes.nexassearch.com)
            if len(domain_parts) > 2:
                subdomain = domain_parts[0]

        if subdomain and subdomain != 'www':
            logger.debug("Subdomain detected: %s", subdomain)
            request.subdomain = subdomain
            request.urlconf = 'storefront.urls'
        else:
            logger.debug("No subdomain detected, using main site.")
            request.subdomain = None