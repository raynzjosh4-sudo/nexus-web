import os
import django
from django.conf import settings
from django.test import RequestFactory
from core.middleware import SubdomainMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

factory = RequestFactory()
host = 'chill.nexassearch.com'
request = factory.get('/sitemap.xml', HTTP_HOST=host)

print(f"Testing host: {host}")

# Manually run middleware logic
middleware = SubdomainMiddleware(lambda r: None)
middleware(request)

print(f"Extracted subdomain: '{request.subdomain}'")

if request.subdomain == 'chill':
    print("✅ Middleware working correctly")
else:
    print(f"❌ Middleware failed. Expected 'chill', got '{request.subdomain}'")
