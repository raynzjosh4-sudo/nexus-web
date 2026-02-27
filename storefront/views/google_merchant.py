"""
Google Merchant Center Data Feed Generator

Generates product CSV/XML feed for Google Shopping with all required attributes:
- Product ID
- Title
- Description  
- Link (product URL)
- Image Link
- Price
- Availability
- Brand (✅ NEW)
- GTIN (✅ NEW - barcode/EAN)
- MPN (✅ NEW - manufacturer part number)
"""

import csv
import json
import logging
from io import StringIO
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.template.loader import render_to_string
from ..client import get_supabase_client

logger = logging.getLogger(__name__)


def format_date(date_str):
    """Format date to YYYY-MM-DD."""
    if not date_str:
        return ''
    try:
        if isinstance(date_str, str):
            return date_str[:10]
        return date_str.strftime('%Y-%m-%d')
    except:
        return ''


@cache_page(60 * 60 * 24)  # Cache for 24 hours
def export_google_merchant_csv(request, subdomain=None):
    """
    Export products as CSV for Google Merchant Center.
    
    Call: GET /merchant/products.csv (subdomain-specific)
    
    Columns:
    - Product ID (posts.id)
    - Title (data.productName)
    - Description (data.textContent)
    - Link (product URL)
    - Image Link (data.images[0].url)
    - Price (data.productPrice data.productCurrency)
    - Availability (posts.stock_status)
    - Brand (data.brand) ✅ NEW
    - GTIN (data.gtin) ✅ NEW
    - MPN (data.mpi) ✅ NEW
    """
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        return HttpResponse('Subdomain required', status=400)
    
    try:
        supabase = get_supabase_client()
        
        # Fetch business
        biz_response = supabase.table('business_profiles')\
            .select('*')\
            .eq('domain', subdomain)\
            .execute()
        
        if not biz_response.data:
            return HttpResponse('Business not found', status=404)
        
        business = biz_response.data[0]
        business_id = business.get('id')
        
        # Fetch products
        posts_response = supabase.table('posts')\
            .select('*')\
            .eq('business_id', business_id)\
            .order('updated_at', desc=True)\
            .limit(50000)\
            .execute()
        
        # Generate CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'ID',
            'Title',
            'Description',
            'Link',
            'Image Link',
            'Price',
            'Currency',
            'Availability',
            'Brand',
            'GTIN',
            'MPN',
        ])
        writer.writeheader()
        
        for post in posts_response.data:
            post_data = post.get('data', {})
            if isinstance(post_data, str):
                post_data = json.loads(post_data)
            
            # Get images
            images = post_data.get('images', [])
            image_url = ''
            if images and isinstance(images, list) and len(images) > 0:
                first_img = images[0]
                image_url = first_img.get('url') if isinstance(first_img, dict) else str(first_img)
            
            # Fallback image
            if not image_url:
                image_url = post_data.get('thumbnailUrl') or post_data.get('imageUrl') or ''
            
            availability = post.get('stock_status', 'in_stock')
            if availability == 'in_stock':
                availability = 'in stock'
            elif availability == 'out_of_stock':
                availability = 'out of stock'
            else:
                availability = 'preorder'
            
            writer.writerow({
                'ID': post.get('id'),
                'Title': post_data.get('productName', 'Untitled'),
                'Description': post_data.get('textContent', '')[:5000],  # Google limit: 5000 chars
                'Link': request.build_absolute_uri(f'/product/{post["id"]}/'),
                'Image Link': image_url,
                'Price': post_data.get('productPrice', 0),
                'Currency': post_data.get('productCurrency', 'UGX'),
                'Availability': availability,
                'Brand': post_data.get('brand', ''),                    # ✅ NEW
                'GTIN': post_data.get('gtin', ''),                      # ✅ NEW
                'MPN': post_data.get('mpi', ''),                        # ✅ NEW
            })
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="google-merchant-{subdomain}.csv"'
        return response
        
    except Exception as e:
        logger.exception(f'Error generating merchant CSV for {subdomain}: {e}')
        return HttpResponse(f'Error: {str(e)}', status=500)


@cache_page(60 * 60 * 24)  # Cache for 24 hours
def export_google_merchant_xml(request, subdomain=None):
    """
    Export products as XML for Google Merchant Center (alternative format).
    
    Call: GET /merchant/products.xml
    """
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        return HttpResponse('Subdomain required', status=400)
    
    try:
        supabase = get_supabase_client()
        
        # Fetch business
        biz_response = supabase.table('business_profiles')\
            .select('*')\
            .eq('domain', subdomain)\
            .execute()
        
        if not biz_response.data:
            return HttpResponse('Business not found', status=404)
        
        business = biz_response.data[0]
        business_id = business.get('id')
        
        # Fetch products
        posts_response = supabase.table('posts')\
            .select('*')\
            .eq('business_id', business_id)\
            .order('updated_at', desc=True)\
            .limit(50000)\
            .execute()
        
        products = []
        for post in posts_response.data:
            post_data = post.get('data', {})
            if isinstance(post_data, str):
                post_data = json.loads(post_data)
            
            # Get images
            images = post_data.get('images', [])
            image_url = ''
            if images and isinstance(images, list) and len(images) > 0:
                first_img = images[0]
                image_url = first_img.get('url') if isinstance(first_img, dict) else str(first_img)
            
            if not image_url:
                image_url = post_data.get('thumbnailUrl') or post_data.get('imageUrl') or ''
            
            availability = post.get('stock_status', 'in_stock')
            if availability == 'in_stock':
                availability = 'in stock'
            elif availability == 'out_of_stock':
                availability = 'out of stock'
            else:
                availability = 'preorder'
            
            products.append({
                'id': post.get('id'),
                'title': post_data.get('productName', 'Untitled'),
                'description': post_data.get('textContent', '')[:5000],
                'link': request.build_absolute_uri(f'/product/{post["id"]}/'),
                'image_link': image_url,
                'price': post_data.get('productPrice', 0),
                'currency': post_data.get('productCurrency', 'UGX'),
                'availability': availability,
                'brand': post_data.get('brand', ''),
                'gtin': post_data.get('gtin', ''),
                'mpi': post_data.get('mpi', ''),
            })
        
        xml_content = render_to_string('storefront/merchant_products.xml', {
            'products': products,
            'business_name': business.get('business_name'),
        })
        
        return HttpResponse(xml_content, content_type='application/xml')
        
    except Exception as e:
        logger.exception(f'Error generating merchant XML for {subdomain}: {e}')
        return HttpResponse(f'Error: {str(e)}', status=500)
