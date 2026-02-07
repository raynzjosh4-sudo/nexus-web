"""Middleware to parse subdomain from request host and attach it to the request.

Sets `request.subdomain` to a string (e.g. 'alice') or None for bare/root domains.
"""
from typing import Optional

from django.conf import settings


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _extract_subdomain(self, host: str) -> Optional[str]:
        host = (host or '').split(':')[0]
        if not host:
            return None

        # Primary domain we expect
        primary = 'nexassearch.com'

        # Exact match -> no subdomain
        if host == primary or host.endswith('.' + primary):
            if host == primary:
                return None
            # strip the primary domain
            sub = host[: -len('.' + primary)]
            return sub if sub else None

        # Support localhost subdomains when enabled via settings
        if getattr(settings, 'ALLOW_LOCALHOST_SUBDOMAINS', True):
            if host.endswith('.localhost'):
                sub = host[: -len('.localhost')]
                return sub if sub else None

        # Generic fallback: if there are more than two labels, treat the leftmost parts as subdomain
        parts = host.split('.')
        if len(parts) > 2:
            return '.'.join(parts[:-2])

        return None

    def __call__(self, request):
        try:
            host = request.get_host()
        except Exception:
            host = ''

        request.full_host = host
        request.subdomain = self._extract_subdomain(host)

        response = self.get_response(request)
        return response
