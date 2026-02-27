import json
import logging
from django.shortcuts import render, redirect
from django.http import Http404
from ..client import get_supabase_client
from ..utils.component_renderer import render_component_list 


logger = logging.getLogger(__name__)

def normalize_component_data(component):
    """
    Standardizes component types so they match exactly what the HTML template expects.
    """
    if not isinstance(component, dict):
        return component

    raw_type = component.get('type', '')
    
    # 1. Basic cleaning (ProfileServicesComponent -> services)
    clean = raw_type.replace('Profile', '').replace('Component', '').lower()
    
    # 2. EXPLICIT MAPPING (The Fix for "Missing Components")
    # This maps what the DB gives -> what your HTML {% elif %} checks for.
    type_mapping = {
        'services': 'servicelist',
        'service': 'servicelist',
        'servicelist': 'servicelist',
        
        'features': 'featurelist',
        'feature': 'featurelist',
        'featurelist': 'featurelist',
        
        'downloads': 'filedownload',
        'download': 'filedownload',
        'filedownload': 'filedownload',
        'files': 'filedownload',
        
        'tabs': 'tabbedcontent',
        'tab': 'tabbedcontent',
        'tabbedcontent': 'tabbedcontent',
        
        'gallery': 'gallery',
        'images': 'gallery',
        
        'websitetheme': 'webtheme',
        'webtheme': 'webtheme',
        'theme': 'webtheme',
        'profilewebsitethemecomponent': 'webtheme',
    }

    # Apply mapping. If not found in mapping, use the cleaned string.
    component['clean_type'] = type_mapping.get(clean, clean)

    # 3. Component-Specific Fixes
    if component['clean_type'] == 'gallery':
        if 'imageUrls' not in component:
            component['imageUrls'] = component.get('images') or component.get('items') or []
    
    if component['clean_type'] == 'testimonial':
        testimonials = component.get('testimonials', [])
        for t in testimonials:
            if 'authorImageUrl' not in t and 'imageUrl' in t:
                t['authorImageUrl'] = t['imageUrl']

    # 4. Recursive Fix for Tabs
    if component['clean_type'] == 'tabbedcontent':
        for tab in component.get('tabs', []):
            tab_sub_components = tab.get('components', [])
            tab['components'] = [normalize_component_data(sub) for sub in tab_sub_components]
            
    return component

def shop_home(request):
    subdomain = getattr(request, 'subdomain', None)
    
    # If no subdomain, render the main landing page with all businesses
    if not subdomain:
        supabase = get_supabase_client()
        
        # Fetch all businesses (both verified and unverified)
        businesses_response = supabase.table('business_profiles').select('*').order('created_at', desc=True).execute()
        businesses = businesses_response.data or []
        
        # Separate verified and unverified
        verified_businesses = [b for b in businesses if b.get('is_verified', False)]
        unverified_businesses = [b for b in businesses if not b.get('is_verified', False)]
        
        # Fetch trending news (latest 4 articles)
        try:
            news_response = supabase.table('news_articles').select('*, news_authors(name, avatar_url, is_verified)').order('published_at', desc=True).limit(4).execute()
            trending_news = news_response.data or []
        except Exception as e:
            logger.warning(f"Could not fetch trending news: {e}")
            trending_news = []
        
        # Fetch lost items (latest 4)
        try:
            lost_items_response = supabase.table('lost_found_items').select('*').order('created_at', desc=True).limit(4).execute()
            lost_items = lost_items_response.data or []
        except Exception as e:
            logger.warning(f"Could not fetch lost items: {e}")
            lost_items = []
        
        # Fetch community posts (latest 4)
        try:
            community_response = supabase.table('community_posts').select('*, nexususers!community_posts_nexususers_fkey(name, avatar_url)').order('created_at', desc=True).limit(4).execute()
            community_posts = community_response.data or []
        except Exception as e:
            logger.warning(f"Could not fetch community posts: {e}")
            community_posts = []
        
        context = {
            'verified_businesses': verified_businesses,
            'unverified_businesses': unverified_businesses,
            'total_businesses': len(businesses),
            'trending_news': trending_news,
            'lost_items': lost_items,
            'community_posts': community_posts,
        }
        
        return render(request, 'storefront/main_landing.html', context)

    supabase = get_supabase_client()
    search_query = request.GET.get('q', '').strip()

    # 1. Fetch Business Profile
    response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    if not response.data:
        raise Http404(f"Shop '{subdomain}' not found.")

    business_data = response.data[0]
    business_id = business_data.get('id')

    # 2. Fetch Products
    posts_query = supabase.table('posts')\
        .select('*, categories(name)')\
        .eq('business_id', business_id)

    if search_query:
        posts_query = posts_query.ilike('data->>productName', f"%{search_query}%")
        
    posts_response = posts_query.order('created_at', desc=True).execute()

    # --- PROCESS PRODUCTS ---
    products_by_category = {}
    for post in posts_response.data:
        post_data = post.get('data', {})
        
        # Category Logic
        cat_linked = post.get('categories') 
        if cat_linked and isinstance(cat_linked, dict):
             cat_name = cat_linked.get('name', 'General')
        else:
            cat_info = post_data.get('category')
            cat_name = cat_info.get('name', 'General') if isinstance(cat_info, dict) else 'General'
        
        cat_name = cat_name.title()

        # Image Logic
        display_image = None
        images_list = post_data.get('images', [])
        if images_list and isinstance(images_list, list) and len(images_list) > 0:
            first = images_list[0]
            display_image = first.get('url') if isinstance(first, dict) else str(first)
        if not display_image: display_image = post_data.get('thumbnailUrl')
        if not display_image: display_image = post_data.get('imageUrl')

        p_name = post_data.get('productName') or post_data.get('name') or post_data.get('title') or 'Untitled'
        
        product_obj = {
            'id': post.get('id'),
            'name': p_name, 
            'productName': p_name,
            'description': post_data.get('textContent', ''),
            'price': post_data.get('productPrice', 0),
            'currency': post_data.get('productCurrency', 'UGX'),
            'image_url': display_image,
        }

        if cat_name not in products_by_category:
            products_by_category[cat_name] = []
        products_by_category[cat_name].append(product_obj)

    # 3. Handle Business Components
    components_raw = business_data.get('components')
    biz_components = []
    
    if isinstance(components_raw, str):
        try:
            biz_components = json.loads(components_raw) or []
        except: 
            biz_components = []
    elif isinstance(components_raw, list):
        biz_components = components_raw

    # Normalize EVERY component (including those inside tabs)
    biz_components = [normalize_component_data(c) for c in biz_components]

    # Separate Components for layout
    hero_component = next((c for c in biz_components if c['clean_type'] == 'hero'), None)
    tab_component = next((c for c in biz_components if c['clean_type'] == 'tabbedcontent'), None)
    theme_component = next((c for c in biz_components if c['clean_type'] == 'webtheme'), None)
    
    # Everything else goes into the main stack
    other_components = [c for c in biz_components if c['clean_type'] not in ['hero', 'tabbedcontent', 'webtheme']]


    # Render components
    render_ctx = {'business': business_data}
    hero_html = render_component_list([hero_component], render_ctx) if hero_component else ""
    tabs_html = render_component_list([tab_component], render_ctx) if tab_component else ""
    components_html = render_component_list(other_components, render_ctx)

    # Fetch business reviews for aggregateRating
    reviews_response = supabase.table('reviews').select('rating').eq('product_id', business_id).execute()
    if reviews_response.data:
        ratings = [r.get('rating', 0) for r in reviews_response.data]
        business_data['reviews_count'] = len(ratings)
        business_data['reviews_avg'] = sum(ratings) / len(ratings) if ratings else 0
    else:
        business_data['reviews_count'] = 0
        business_data['reviews_avg'] = 0

    context = {
        'business': business_data,
        'hero_component': hero_component,
        'hero_html': hero_html,
        'tab_component': tab_component,
        'tabs_html': tabs_html,
        'components': other_components,
        'components_html': components_html,
        'products_by_category': products_by_category,
        'search_query': search_query,
        'theme_component': theme_component,
        'user': {},  # Initialize empty user dict (will be populated if user is logged in)
    }
    
    # If user is logged in, fetch their session data
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user_res = supabase.table('nexususers').select('*').eq('id', user_id).execute()
            if user_res.data:
                context['user'] = user_res.data[0]
        except Exception as e:
            logger.warning(f"Could not fetch user data: {e}")
            context['user'] = {'name': request.session.get('user_email', 'User')}

    # Breadcrumbs for structured data (Home -> Shop)
    context['breadcrumbs'] = [
        {'name': 'Home', 'url': f"{request.scheme}://{request.get_host}/"},
        {'name': business_data.get('business_name', 'Store'), 'url': request.build_absolute_uri}
    ]
    
    return render(request, 'storefront/shop_home.html', context) 