from django.shortcuts import render, redirect
from ..client import get_supabase_client
from .auth import _get_business_context
import logging

logger = logging.getLogger(__name__)

def profile_view(request):
    uid = request.session.get('user_id')
    logger.debug(f"Profile View: Accessing profile for user_id: {uid}")
    
    if not uid:
        logger.warning("Profile View: No user_id in session, redirecting to login")
        return redirect('login') 
    
    supabase = get_supabase_client()
    
    # 1. User Profile Data
    user_data = {}
    try:
        u_res = supabase.table('nexususers').select('*').eq('id', uid).execute()
        if u_res.data:
            user_data = u_res.data[0]
            logger.debug(f"Profile View: Found nexususer record for {uid}")
        else:
            user_data = {'name': 'Nexus User', 'email': request.session.get('user_email')}
            logger.debug(f"Profile View: No nexususer record for {uid}, using session fallback")
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        user_data = {'name': 'Nexus User', 'email': request.session.get('user_email')}

    # 2. Orders (Market Orders) - Hydrated with product & business details
    orders = []
    try:
        o_res = supabase.table('market_orders').select('*').eq('buyer_id', uid).order('created_at', desc=True).execute()
        orders = o_res.data
        logger.debug(f"Profile View: Fetched {len(orders)} orders for user {uid}")
        
        if orders:
            # Get unique product and business IDs
            product_ids = list(set([o['product_id'] for o in orders if o.get('product_id')]))
            business_ids = list(set([o['business_id'] for o in orders if o.get('business_id')]))
            
            logger.debug(f"Profile View: Hydrating {len(product_ids)} unique products and {len(business_ids)} businesses")

            # Map products
            p_map = {}
            if product_ids:
                p_res = supabase.table('posts').select('id, data').in_('id', product_ids).execute()
                for p in p_res.data:
                    p_map[p['id']] = p.get('data', {})
                logger.debug(f"Profile View: Found {len(p_res.data)} product records in 'posts'")
            
            # Map businesses
            b_map = {}
            if business_ids:
                b_res = supabase.table('business_profiles').select('id, business_name, logo_url').in_('id', business_ids).execute()
                for b in b_res.data:
                    b_map[b['id']] = b
                logger.debug(f"Profile View: Found {len(b_res.data)} business records")

            for o in orders:
                p_data = p_map.get(o['product_id'], {})
                o['product_name'] = p_data.get('productName', 'Untitled Product')
                o['product_image'] = p_data.get('thumbnailUrl') or p_data.get('imageUrl')
                o['product_currency'] = p_data.get('productCurrency', 'UGX')
                
                biz = b_map.get(o['business_id'], {})
                o['business_name'] = biz.get('business_name', 'Official Store')
                o['business_logo'] = biz.get('logo_url')
                
    except Exception as e:
        logger.error(f"Orders hydration error: {e}")

    # 3. Wishlist Details
    wishes = []
    try:
        w_res = supabase.table('wishlists').select('product_id').eq('user_id', uid).execute()
        w_ids = [w['product_id'] for w in w_res.data]
        logger.debug(f"Profile View: Found {len(w_ids)} wishlist IDs for user {uid}")
        
        if w_ids:
            p_res = supabase.table('posts').select('*').in_('id', w_ids).execute()
            for p in p_res.data:
                p_data = p.get('data', {})
                
                # Robust image logic
                display_image = None
                img_list = p_data.get('images', [])
                if isinstance(img_list, list) and img_list:
                    first = img_list[0]
                    display_image = first.get('url') if isinstance(first, dict) else first
                if not display_image:
                    display_image = p_data.get('thumbnailUrl') or p_data.get('imageUrl')

                wishes.append({
                    'id': p['id'],
                    'name': p_data.get('productName', 'Untitled Product'),
                    'price': p_data.get('productPrice', 0),
                    'currency': p_data.get('productCurrency', 'UGX'),
                    'image_url': display_image
                })
            logger.debug(f"Profile View: Successfully hydrated {len(wishes)} wishlist items")
    except Exception as e:
        logger.error(f"Wishlist hydration error: {e}")

    # 4. Global Business Context (Store Branding)
    business_ctx = _get_business_context(request)
    
    # If no store branding (e.g. on main domain), check if current user has their own business theme
    if not business_ctx or not business_ctx.get('theme_component'):
        try:
            from .shop import normalize_component_data
            b_res = supabase.table('business_profiles').select('*').eq('user_id', uid).execute()
            if b_res.data:
                biz = b_res.data[0]
                comps = biz.get('components', [])
                if isinstance(comps, str):
                    import json
                    try: comps = json.loads(comps) or []
                    except: comps = []
                
                # Normalize and find theme
                for c in comps:
                    normalized = normalize_component_data(c)
                    if normalized.get('clean_type') == 'webtheme':
                        biz['theme_component'] = normalized
                        business_ctx = biz
                        break
        except Exception as be:
            logger.error(f"User business theme fetch error: {be}")

    return render(request, 'storefront/profile.html', {
        'business': business_ctx,
        'theme_component': business_ctx.get('theme_component'),
        'user': user_data,
        'orders': orders,
        'wishes': wishes,
        'debug_info': {
            'uid': uid,
            'order_count': len(orders),
            'wish_count': len(wishes)
        }
        , 'breadcrumbs': [
            {'name': 'Home', 'url': f"{request.scheme}://{request.get_host()}/"},
            {'name': 'Profile', 'url': request.build_absolute_uri}
        ]
    })
