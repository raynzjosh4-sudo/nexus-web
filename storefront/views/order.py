from django.shortcuts import render
from django.http import Http404
from ..client import get_supabase_client


def order_confirmation(request, order_id):
    """Display order confirmation with Order and ParcelDelivery JSON-LD."""
    subdomain = getattr(request, 'subdomain', None)
    
    supabase = get_supabase_client()
    
    # Fetch business
    biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    if not biz_response.data:
        raise Http404("Shop not found")
    
    business = biz_response.data[0]
    
    # Fetch order
    order_response = supabase.table('market_orders').select('*').eq('id', str(order_id)).execute()
    if not order_response.data:
        raise Http404("Order not found")
    
    order = order_response.data[0]
    
    # Fetch product
    product_response = supabase.table('posts').select('*').eq('id', str(order['product_id'])).execute()
    product = product_response.data[0] if product_response.data else None
    
    # Extract product data
    if product:
        product_data = product.get('data', {})
        product_obj = {
            'id': product['id'],
            'name': product_data.get('productName', 'Product'),
            'price': product_data.get('productPrice', 0),
            'currency': product_data.get('productCurrency', 'UGX'),
            'image_url': product_data.get('thumbnailUrl') or product_data.get('imageUrl'),
        }
    else:
        product_obj = None
    
    context = {
        'business': business,
        'order': order,
        'product': product_obj,
        'buyer_name': request.session.get('user_name', 'Customer'),
        'buyer_address': order.get('buyer_address', ''),
        'theme_component': {'backgroundColor': '#121418', 'surfaceColor': '#181b21', 'textColor': '#ffffff', 'secondaryTextColor': '#9ca3af', 'accentColor': '#f97316'},
    }
    
    return render(request, 'storefront/order_confirmation.html', context)
