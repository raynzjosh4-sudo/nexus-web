import json
import logging
from django.shortcuts import render, redirect
from django.http import Http404
from ..client import get_supabase_client
from .shop import normalize_component_data

logger = logging.getLogger(__name__)


# ISO 4217 Valid Currency Codes (common in Africa/EastAfrica)
VALID_CURRENCY_CODES = {
    'UGX',  # Uganda Shilling (primary)
    'USD',  # US Dollar
    'EUR',  # Euro
    'GBP',  # British Pound
    'KES',  # Kenyan Shilling
    'TZS',  # Tanzanian Shilling
    'RWF',  # Rwandan Franc
    'BDI',  # Burundian Franc
    'ZAR',  # South African Rand
    'NGN',  # Nigerian Naira
    'EGP',  # Egyptian Pound
    'MAD',  # Moroccan Dirham
    'GHS',  # Ghanaian Cedis
    'ZWL',  # Zimbabwean Dollar
    'ZMW',  # Zambian Kwacha
    'ETB',  # Ethiopian Birr
    'AED',  # UAE Dirham
    'INR',  # Indian Rupee
    'PKR',  # Pakistani Rupee
}


def validate_currency(currency_input):
    """
    Validate and normalize currency code to ISO 4217 standard.
    
    Args:
        currency_input: Raw currency string from database
    
    Returns:
        Valid ISO 4217 currency code (uppercase) or 'UGX' if invalid
    
    Examples:
        validate_currency('UGX')    → 'UGX'
        validate_currency('usd ')   → 'USD'
        validate_currency('INVALID') → 'UGX' (logs warning)
        validate_currency(None)     → 'UGX'
    """
    if not currency_input:
        return 'UGX'  # Default fallback
    
    # Clean: strip whitespace and convert to uppercase
    clean = str(currency_input).strip().upper()
    
    # Check if valid
    if clean in VALID_CURRENCY_CODES:
        return clean
    
    # Invalid - log warning and return default
    logger.warning(f"Invalid currency code detected: '{currency_input}' → defaulting to 'UGX'")
    return 'UGX'


def get_theme_component(business_data):
    """
    Extract the theme component from business components.
    Returns the theme component dict or a sensible default dark theme if not found.
    """
    import json
    components_raw = business_data.get('components')
    biz_components = []
    
    # 1. robust parsing
    if isinstance(components_raw, str):
        try:
            biz_components = json.loads(components_raw) or []
        except json.JSONDecodeError:
            print("Error decoding components JSON")
            biz_components = []
    elif isinstance(components_raw, list):
        biz_components = components_raw
    else:
        print(f"Unknown components type: {type(components_raw)}")
        # Return default theme if can't parse
        return _get_default_theme()

    print(f"Searching for theme in {len(biz_components)} components...")
    
    # 2. Iterate and check
    for c in biz_components:
        if not isinstance(c, dict):
            continue
            
        raw_type = c.get('type', '')
        # Check raw type directly first (Most reliable)
        if raw_type == 'ProfileWebsiteThemeComponent':
            print(f"Found theme by raw type: {c.get('type')}")
            return c
            
        # Check normalized/cleaned types
        try:
            normalized = normalize_component_data(c.copy())
            clean_type = normalized.get('clean_type', '')
            
            if clean_type in ('websitetheme', 'webtheme'):
                print(f"Found theme by cleanup: {clean_type} (was {raw_type})")
                return c
        except Exception as e:
            print(f"Error normalizing component {raw_type}: {e}")
            continue
    
    print("No theme component found. Using default theme.")
    return _get_default_theme()


def _get_default_theme():
    """
    Return a sensible default dark theme when no theme is configured.
    """
    return {
        'type': 'ProfileWebsiteThemeComponent',
        'backgroundColor': '#121418',
        'surfaceColor': '#181b21',
        'textColor': '#ffffff',
        'secondaryTextColor': '#9ca3af',
        'accentColor': '#f97316',
        'secondaryColor': '#DA03D0',
    }

def product_detail(request, product_id):
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        return redirect('http://localhost:8000') 

    supabase = get_supabase_client()

    # Fetch Business
    biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    if not biz_response.data:
        raise Http404("Shop not found")
    business_data = biz_response.data[0]
    
    # Parse and normalize components for theme detection
    components_raw = business_data.get('components', [])
    if isinstance(components_raw, str):
        try: components_raw = json.loads(components_raw) or []
        except: components_raw = []
    
    business_data['components'] = [normalize_component_data(c) for c in components_raw if isinstance(c, dict)]

    # Fetch Product
    prod_response = supabase.table('posts').select('*, categories(name)').eq('id', str(product_id)).execute()
    if not prod_response.data:
        raise Http404("Product not found")

    post = prod_response.data[0]
    post_data = post.get('data', {})

    # Category Logic
    cat_linked = post.get('categories')
    if cat_linked and isinstance(cat_linked, dict):
         cat_name = cat_linked.get('name', 'General')
    else:
        cat_data = post_data.get('category') or {}
        cat_name = cat_data.get('name', 'General') if isinstance(cat_data, dict) else 'General'

    # Components Parsing
    components = post_data.get('components', [])
    if isinstance(components, str):
        try:
            components = json.loads(components) or []
        except json.JSONDecodeError:
            components = []

    # Markdown rendering
    try:
        import markdown as _md
        for c in components:
            if isinstance(c, dict) and c.get('type') == 'RichTextComponent' and c.get('markdownText'):
                try:
                    c['markdownText'] = _md.markdown(c['markdownText'])
                except Exception:
                    pass
    except ImportError:
        pass # Markdown not installed

    # Images
    images_raw = post_data.get('images') or []
    images = []
    if isinstance(images_raw, list):
        for it in images_raw:
            if isinstance(it, dict) and 'url' in it:
                images.append(it)
            elif isinstance(it, str):
                images.append({'url': it})

    display_image = images[0].get('url') if images else (post_data.get('thumbnailUrl') or post_data.get('imageUrl'))

    # Fetch reviews for this product
    reviews_response = supabase.table('reviews').select('rating').eq('product_id', str(product_id)).execute()
    reviews_count = 0
    reviews_avg = 0
    if reviews_response.data:
        ratings = [r.get('rating', 0) for r in reviews_response.data]
        reviews_count = len(ratings)
        reviews_avg = sum(ratings) / len(ratings) if ratings else 0

    product = {
        'id': post.get('id'),
        'name': post_data.get('productName', 'Untitled'),
        'productName': post_data.get('productName', post.get('title')),
        'description': post_data.get('textContent', ''),
        'price': post_data.get('productPrice', 0),
        'currency': validate_currency(post_data.get('productCurrency')),  # ✅ VALIDATED
        'image_url': display_image,
        'images': images,
        'video_url': post_data.get('videoUrl'),
        'components': components,
        'category': {'name': cat_name},
        'comments': post_data.get('comments') or [],
        'author': post_data.get('author') or {},
        'timestamp': post_data.get('timestamp') or post.get('created_at'),
        'reviews_count': reviews_count,
        'reviews_avg': reviews_avg,
        'brand': post_data.get('brand', ''),                    # ✅ NEW
        'gtin': post_data.get('gtin', ''),                      # ✅ NEW (barcode/EAN)
        'mpi': post_data.get('mpi', ''),                        # ✅ NEW (manufacturer part number)
    }

    # Schema helpers: detect swap mode (heuristic) and provide schema-friendly fields
    is_swap = False
    try:
        if (product.get('price') == 0) or ('swap' in (product.get('name') or '').lower()) or ('trade' in (product.get('name') or '').lower()):
            is_swap = True
    except Exception:
        is_swap = False

    product['is_swap'] = is_swap
    # For structured data use a clear title and price
    product['schema_name'] = (f"Swap: {product['name']}" if is_swap else product['name'])
    product['schema_price'] = 0 if is_swap else product.get('price', 0)


    # Fetch Related Products
    related_products = []
    posts_query = supabase.table('posts').select('*').eq('business_id', business_data.get('id')).order('created_at', desc=True).limit(20)
    related_response = posts_query.execute()
    
    for p in related_response.data:
        if p.get('id') == str(product_id): continue 
        p_data = p.get('data', {})
        p_cat = p_data.get('category', {}).get('name', 'General')
        
        # Fetch reviews for related product
        p_reviews_response = supabase.table('reviews').select('rating').eq('product_id', str(p['id'])).execute()
        p_reviews_count = 0
        p_reviews_avg = 0
        if p_reviews_response.data:
            p_ratings = [r.get('rating', 0) for r in p_reviews_response.data]
            p_reviews_count = len(p_ratings)
            p_reviews_avg = sum(p_ratings) / len(p_ratings) if p_ratings else 0
        
        if p_cat == cat_name:
            img = p_data.get('thumbnailUrl') or p_data.get('imageUrl')
            if p_data.get('images') and len(p_data['images']) > 0:
                first = p_data['images'][0]
                img = first.get('url') if isinstance(first, dict) else first

            related_products.append({
                'id': p.get('id'),
                'name': p_data.get('productName'),
                'price': p_data.get('productPrice'),
                'currency': validate_currency(p_data.get('productCurrency')),  # ✅ VALIDATED
                'image_url': img,
                'category': p_cat,
                'reviews_count': p_reviews_count,
                'reviews_avg': p_reviews_avg,
            })
            if len(related_products) >= 5: break


    from ..utils.component_renderer import render_component_list

    # Render Components to HTML
    product['components_html'] = render_component_list(components)

    context = {
        'business': business_data,
        'product': product,
        'related_products': related_products,
        'theme_component': get_theme_component(business_data),
    }
    # Breadcrumbs for product pages: Home -> Category -> Product
    try:
        from urllib.parse import quote
        cat_name = product.get('category', {}).get('name', 'Category')
        cat_slug = quote(cat_name)
        category_url = f"{request.scheme}://{request.get_host()}/category/{cat_slug}/"
    except Exception:
        category_url = request.build_absolute_uri

    context['breadcrumbs'] = [
        {'name': 'Home', 'url': f"{request.scheme}://{request.get_host()}/"},
        {'name': product.get('category', {}).get('name', 'Category'), 'url': category_url},
        {'name': product['name'], 'url': request.build_absolute_uri}
    ]
    
    return render(request, 'storefront/partials/mainstore/product_detail.html', context)

def category_view(request, category_name):
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        return redirect('http://localhost:8000')

    supabase = get_supabase_client()
    
    biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    if not biz_response.data:
        raise Http404("Shop not found")
    business_data = biz_response.data[0]
    business_id = business_data.get('id')

    # Normalize components for theme detection
    components_raw = business_data.get('components', [])
    if isinstance(components_raw, str):
        try: components_raw = json.loads(components_raw) or []
        except: components_raw = []
    
    business_data['components'] = [normalize_component_data(c) for c in components_raw if isinstance(c, dict)]
    
    # Get Theme
    theme_component = get_theme_component(business_data)

    cat_resp = supabase.table('categories').select('id').ilike('name', category_name).execute()
    
    products = []
    if cat_resp.data:
        cat_id = cat_resp.data[0]['id']
        posts_resp = supabase.table('posts').select('*').eq('business_id', business_id).eq('category_id', cat_id).execute()

        for post in posts_resp.data:
            post_data = post.get('data', {})
            img = post_data.get('thumbnailUrl') or post_data.get('imageUrl')
            if post_data.get('images') and len(post_data['images']) > 0:
                first = post_data['images'][0]
                img = first.get('url') if isinstance(first, dict) else first
            
            products.append({
                'id': post['id'],
                'name': post_data.get('productName', 'Untitled'),
                'price': post_data.get('productPrice', 0),
                'currency': validate_currency(post_data.get('productCurrency')),  # ✅ VALIDATED
                'image_url': img,
                'video_url': post_data.get('videoUrl'),
            })

    context = {
        'business': business_data,
        'theme_component': theme_component,
        'category_name': category_name,
        'products': products
    }
    # Breadcrumbs for category pages
    from urllib.parse import quote
    context['breadcrumbs'] = [
        {'name': 'Home', 'url': f"{request.scheme}://{request.get_host()}/"},
        {'name': category_name, 'url': f"{request.scheme}://{request.get_host()}/category/{quote(category_name)}/"}
    ]

    return render(request, 'storefront/partials/mainstore/category_list.html', context)

def create_order(request, product_id):
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        return redirect('http://localhost:8000')

    supabase = get_supabase_client()

    # Fetch Business with error handling
    try:
        biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
        if not biz_response.data:
            raise Http404("Shop not found")
        business_data = biz_response.data[0]
        business_id = business_data.get('id')
    except Exception as e:
        logger.error(f"Error fetching business: {e}")
        raise Http404("Shop not found")

    # Fetch Product with error handling
    try:
        prod_response = supabase.table('posts').select('*').eq('id', str(product_id)).execute()
        if not prod_response.data:
            raise Http404("Product not found")
        post = prod_response.data[0]
        post_data = post.get('data', {})
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise Http404("Product not found")

    # Images logic for preview
    images_raw = post_data.get('images') or []
    display_image = None
    if isinstance(images_raw, list) and images_raw:
        first = images_raw[0]
        display_image = first.get('url') if isinstance(first, dict) else first
    if not display_image:
        display_image = post_data.get('thumbnailUrl') or post_data.get('imageUrl')

    product = {
        'id': post.get('id'),
        'name': post_data.get('productName', 'Untitled'),
        'description': post_data.get('textContent', ''),
        'price': post_data.get('productPrice', 0),
        'currency': validate_currency(post_data.get('productCurrency')),  # ✅ VALIDATED
        'image_url': display_image,
        'category_id': post.get('category_id'),
    }

    # Get theme component for the order page
    theme_component = get_theme_component(business_data)

    if request.method == 'POST':
        # Authentication check
        user_id = request.session.get('user_id')
        if not user_id:
            return render(request, 'storefront/partials/mainstore/create_order.html', {
                'business': business_data,
                'product': product,
                'theme_component': theme_component,
                'error': 'Please log in to place an order'
            })

        # Get form data
        order_type = request.POST.get('order_type')
        offer_price = request.POST.get('offer_price', '').strip()
        phone = request.POST.get('phone', '').strip()
        note = request.POST.get('note', '').strip()

        # Validation
        errors = []
        
        if not order_type or order_type not in ['BID', 'DEPOSIT', 'FULL']:
            errors.append('Please select a valid order type')
        
        if not phone:
            errors.append('Phone number is required')
        elif len(phone) < 10:
            errors.append('Please enter a valid phone number')
        
        # Price validation
        final_price = 0
        if order_type == 'FULL':
            final_price = float(product['price']) if product['price'] else 0
        elif order_type in ['BID', 'DEPOSIT']:
            if not offer_price:
                errors.append('Please enter your offer price')
            else:
                try:
                    final_price = float(offer_price)
                    if final_price <= 0:
                        errors.append('Offer price must be greater than zero')
                except ValueError:
                    errors.append('Invalid price format')
        
        # If there are validation errors, return them
        if errors:
            return render(request, 'storefront/partials/mainstore/create_order.html', {
                'business': business_data,
                'product': product,
                'theme_component': theme_component,
                'errors': errors,
                'form_data': {
                    'order_type': order_type,
                    'offer_price': offer_price,
                    'phone': phone,
                    'note': note
                }
            })

        # Create order
        order_data = {
            'product_id': str(product_id),
            'business_id': business_id,
            'order_type': order_type,
            'offer_price': final_price,
            'buyer_phone': phone,
            'note': note,
            'status': 'PENDING',
            'payment_method': 'CASH',
            'buyer_id': user_id,
        }
        
        # Only add category_id if it exists (matching Dart implementation)
        if product.get('category_id'):
            order_data['category_id'] = product['category_id']
        
        try:
            result = supabase.table('market_orders').insert(order_data).execute()
            logger.info(f"Order created successfully for user {user_id}, product {product_id}")
            
            return render(request, 'storefront/partials/mainstore/create_order.html', {
                'business': business_data,
                'product': product,
                'theme_component': theme_component,
                'success': True,
                'order_id': result.data[0].get('id') if result.data else None
            })
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"Error creating order for user {user_id}: {e}")
            logger.error(f"Full traceback: {error_detail}")
            logger.error(f"Order data that failed: {order_data}")
            return render(request, 'storefront/partials/mainstore/create_order.html', {
                'business': business_data,
                'product': product,
                'theme_component': theme_component,
                'error': f'Unable to place order: {str(e)}'
            })


    return render(request, 'storefront/partials/mainstore/create_order.html', {
        'business': business_data,
        'product': product,
        'theme_component': theme_component,
    })
