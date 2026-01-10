import json
import logging
from django.shortcuts import render, redirect
from django.http import Http404
from ..client import get_supabase_client # Note the ..client (up one level)

logger = logging.getLogger(__name__)

def normalize_component_data(component):
    """
    Helper to ensure components have the right keys for templates.
    Fixes the Gallery 'images' vs 'imageUrls' issue.
    """
    c_type = component.get('type', '')
    
    # --- GALLERY FIX ---
    if 'GalleryComponent' in c_type: 
        # Ensure 'imageUrls' exists
        if 'imageUrls' not in component:
            # Try to find images in other common keys
            raw_images = component.get('images') or component.get('items') or []
            clean_urls = []
            
            # Normalize list of strings or list of objects
            for img in raw_images:
                if isinstance(img, str):
                    clean_urls.append(img)
                elif isinstance(img, dict) and 'url' in img:
                    clean_urls.append(img['url'])
            
            component['imageUrls'] = clean_urls
            
    return component

def shop_home(request):
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        return redirect('http://localhost:8000') 

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

        # Keys Check
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

    # 3. Handle Business Components (THE FIX IS HERE)
    components_raw = business_data.get('components')
    biz_components = []
    
    if isinstance(components_raw, str):
        try:
            biz_components = json.loads(components_raw) or []
        except: 
            biz_components = []
    elif isinstance(components_raw, list):
        biz_components = components_raw

    # Normalize EVERY component before separating them
    biz_components = [normalize_component_data(c) for c in biz_components]

    # Separate Components
    hero_component = next((c for c in biz_components if c.get('type') == 'ProfileHeroComponent'), None)
    tab_component = next((c for c in biz_components if c.get('type') == 'ProfileTabbedContentComponent'), None)
    
    # Filter out Hero and Tab to leave the rest (including Gallery)
    other_components = [c for c in biz_components if c.get('type') not in ['ProfileHeroComponent', 'ProfileTabbedContentComponent']]

    context = {
        'business': business_data,
        'hero_component': hero_component,
        'tab_component': tab_component,
        'components': other_components, # This now contains the normalized Gallery
        'products_by_category': products_by_category,
        'search_query': search_query,
    }
    
    return render(request, 'storefront/shop_home.html', context)