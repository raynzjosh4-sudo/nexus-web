"""
Views for section pages: lost-and-found, community, swap, help
These serve static HTML files from the root directories
"""
from django.shortcuts import render
from django.http import HttpResponse
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
    """Swap section view"""
    try:
        # Read the HTML file from the swap directory
        swap_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'swap',
            'index.html'
        )
        with open(swap_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        logger.error("Swap HTML file not found")
        return HttpResponse('<h1>Page Not Found</h1>', status=404)
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
