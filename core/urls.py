"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
import os

# Custom error view handlers  
def error_500(request):
    """Custom 500 error handler that passes exception details to template"""
    from django.template.response import TemplateResponse
    exception = request.META.get('exc_info', {})
    if isinstance(exception, tuple) and len(exception) >= 2:
        exception_str = str(exception[1])
    else:
        exception_str = "Internal Server Error"
    
    return TemplateResponse(
        request, '500.html', 
        {'exception': exception_str}, 
        status=500
    )

def error_404(request, exception=None):
    """Custom 404 error handler"""
    from django.template.response import TemplateResponse
    return TemplateResponse(
        request, '404.html', 
        {'exception': exception}, 
        status=404
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('storefront.urls')),
]

# Serve static files during development
if settings.DEBUG:
    # Serve /assets/ files
    urlpatterns += [
        re_path(r'^assets/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'assets'),
        }),
        # Serve /js/ files
        re_path(r'^js/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'js'),
        }),
        # Serve /community/detail.html
        re_path(r'^community/detail\.html$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'community'),
            'path': 'detail.html',
        }),
        # Serve /lost-and-found/detail.html
        re_path(r'^lost-and-found/detail\.html$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'lost-and-found'),
            'path': 'detail.html',
        }),
        # Serve /swap/detail.html
        re_path(r'^swap/detail\.html$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'swap'),
            'path': 'detail.html',
        }),
    ]
    # Add default static file serving
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Register custom error handlers
handler404 = error_404
handler500 = error_500

