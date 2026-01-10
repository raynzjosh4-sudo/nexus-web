import json
import logging
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from ..client import get_supabase_client

logger = logging.getLogger(__name__)


@require_POST
def toggle_wishlist(request, product_id):
    """
    Toggle product in/out of user's wishlist.
    Returns JSON response with success status and message.
    """
    # Check authentication
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({
            'success': False,
            'error': 'Please log in to add items to your wishlist',
            'redirect': f'/login/?next={request.path}'
        }, status=401)
    
    try:
        supabase = get_supabase_client()
        
        # Validate product exists
        product_check = supabase.table('posts').select('id').eq('id', str(product_id)).execute()
        if not product_check.data:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            }, status=404)
        
        # Check if already in wishlist
        existing = supabase.table('wishlists').select('*').eq('user_id', user_id).eq('product_id', str(product_id)).execute()
        
        if existing.data:
            # Remove from wishlist
            supabase.table('wishlists').delete().eq('user_id', user_id).eq('product_id', str(product_id)).execute()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'message': 'Removed from wishlist'
            })
        else:
            # Add to wishlist
            wishlist_data = {
                'user_id': user_id,
                'product_id': str(product_id)
            }
            supabase.table('wishlists').insert(wishlist_data).execute()
            return JsonResponse({
                'success': True,
                'action': 'added',
                'message': 'Added to wishlist'
            })
            
    except Exception as e:
        logger.error(f"Wishlist toggle error for user {user_id}, product {product_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to update wishlist. Please try again.'
        }, status=500)


def check_wishlist_status(request, product_id):
    """
    Check if a product is in user's wishlist.
    Returns JSON with in_wishlist boolean.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'in_wishlist': False})
    
    try:
        supabase = get_supabase_client()
        result = supabase.table('wishlists').select('*').eq('user_id', user_id).eq('product_id', str(product_id)).execute()
        
        return JsonResponse({
            'in_wishlist': len(result.data) > 0
        })
    except Exception as e:
        logger.error(f"Wishlist status check error: {e}")
        return JsonResponse({'in_wishlist': False})
