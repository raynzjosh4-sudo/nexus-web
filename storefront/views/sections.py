"""
Views for section pages: lost-and-found, community, swap, help
These serve dynamic pages with user theme colors
"""
from django.shortcuts import render
from django.http import HttpResponse
from ..client import get_supabase_client
import os
import logging

logger = logging.getLogger(__name__)


def lost_and_found_view(request):
    """Lost and Found section view"""
    try:
        # Read the HTML file from the lost-and-found directory
        lost_and_found_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'lost-and-found',
            'index.html'
        )
        with open(lost_and_found_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        logger.error("Lost and Found HTML file not found")
        return HttpResponse('<h1>Page Not Found</h1>', status=404)
    except Exception as e:
        logger.error(f"Error loading Lost and Found page: {e}")
        return HttpResponse('<h1>Error Loading Page</h1>', status=500)


def community_view(request):
    """Community section view"""
    try:
        # Read the HTML file from the community directory
        community_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'community',
            'index.html'
        )
        with open(community_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        logger.error("Community HTML file not found")
        return HttpResponse('<h1>Page Not Found</h1>', status=404)
    except Exception as e:
        logger.error(f"Error loading Community page: {e}")
        return HttpResponse('<h1>Error Loading Page</h1>', status=500)


def swap_view(request):
    """Swap section view - render with user theme colors"""
    try:
        subdomain = getattr(request, 'subdomain', None)
        
        # Fetch business theme if on a subdomain
        theme_component = None
        business = {}
        
        if subdomain:
            supabase = get_supabase_client()
            biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
            
            if biz_response.data:
                business = biz_response.data[0]
                components_raw = business.get('components', [])
                
                # Parse components if needed
                if isinstance(components_raw, str):
                    try:
                        import json
                        components = json.loads(components_raw)
                    except:
                        components = []
                else:
                    components = components_raw or []
                
                # Find theme component
                for comp in components:
                    if isinstance(comp, dict) and comp.get('type', '').lower() in ['webtheme', 'theme']:
                        theme_component = comp
                        break
        
        context = {
            'theme_component': theme_component,
            'business': business
        }
        
        return render(request, 'storefront/swap.html', context)
    except Exception as e:
        logger.error(f"Error loading Swap page: {e}")
        return HttpResponse('<h1>Error Loading Page</h1>', status=500)


def help_view(request):
    """Help section view"""
    try:
        # Read the HTML file from the help directory
        help_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'help',
            'faq.html'
        )
        with open(help_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        logger.error("Help HTML file not found")
        return HttpResponse('<h1>Page Not Found</h1>', status=404)
    except Exception as e:
        logger.error(f"Error loading Help page: {e}")
        return HttpResponse('<h1>Error Loading Page</h1>', status=500)
