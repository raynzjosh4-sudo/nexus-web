from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..client import get_supabase_client
from .shop import normalize_component_data
import logging
import json

logger = logging.getLogger(__name__)

def login_view(request):
    subdomain = getattr(request, 'subdomain', None)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        supabase = get_supabase_client()
        
        try:
            # Authenticate with Supabase (handle multiple response shapes)
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})

            # Debug log the raw response for easier troubleshooting
            logger.debug('Sign-in response: %s', getattr(res, '__dict__', res))

            user = None
            access_token = None

            # Try several common response shapes
            if hasattr(res, 'user') and res.user:
                user = res.user
            elif isinstance(res, dict):
                # supabase-py may return dict with 'data' or 'user'
                user = res.get('user') or (res.get('data') and res['data'].get('user'))
                # Access token might be nested
                access_token = res.get('access_token') or (res.get('data') and res['data'].get('access_token'))
            elif getattr(res, 'data', None):
                # Some SDKs expose a .data property
                data = res.data
                if isinstance(data, dict):
                    user = data.get('user')
                    access_token = data.get('access_token')

            if user:
                # Store session data
                uid = getattr(user, 'id', None) or user.get('id') if isinstance(user, dict) else None
                uemail = getattr(user, 'email', None) or user.get('email') if isinstance(user, dict) else None
                request.session['user_id'] = uid
                request.session['user_email'] = uemail
                if access_token:
                    request.session['access_token'] = access_token

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('shop_home')

        except Exception as e:
            logger.exception("Login failed")
            return render(request, 'storefront/login.html', {
                'error': "Invalid email or password.",
                'business': _get_business_context(request) # Helper to render base template elements
            })
            
    return render(request, 'storefront/login.html', {
        'business': _get_business_context(request)
    })

def signup_view(request):
    subdomain = getattr(request, 'subdomain', None)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            return render(request, 'storefront/signup.html', {
                'error': "Passwords do not match.",
                'business': _get_business_context(request)
            })

        supabase = get_supabase_client()
        
        try:
            res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "display_name": name
                    }
                }
            })

            logger.debug('Signup response: %s', getattr(res, '__dict__', res))

            user = None
            access_token = None
            session_obj = None

            if hasattr(res, 'user') and res.user:
                user = res.user
                session_obj = getattr(res, 'session', None)
            elif isinstance(res, dict):
                user = res.get('user') or (res.get('data') and res['data'].get('user'))
                session_obj = res.get('session') or (res.get('data') and res['data'].get('session'))
                access_token = res.get('access_token') or (res.get('data') and res['data'].get('access_token'))
            elif getattr(res, 'data', None):
                data = res.data
                if isinstance(data, dict):
                    user = data.get('user')
                    session_obj = data.get('session')

            if user:
                # If we received a session or access token, log the user in
                uid = getattr(user, 'id', None) or (user.get('id') if isinstance(user, dict) else None)
                uemail = getattr(user, 'email', None) or (user.get('email') if isinstance(user, dict) else None)
                request.session['user_id'] = uid
                request.session['user_email'] = uemail
                if access_token:
                    request.session['access_token'] = access_token
                if session_obj and isinstance(session_obj, dict):
                    request.session['access_token'] = session_obj.get('access_token') or request.session.get('access_token')

                logger.info(f"Signup Success: {email}")
                return redirect('shop_home')

            # If we reach here, signup likely requires email confirmation
            return render(request, 'storefront/login.html', {
                'error': "Account created! Please check your email to confirm registration.",
                'business': _get_business_context(request)
            })

        except Exception as e:
            logger.error(f"Signup failed: {e}")
            msg = str(e)
            if "already registered" in msg.lower():
                msg = "This email is already registered. Please sign in."
            return render(request, 'storefront/signup.html', {
                'error': msg,
                'business': _get_business_context(request)
            })

    return render(request, 'storefront/signup.html', {
        'business': _get_business_context(request)
    })

def logout_view(request):
    request.session.flush()
    return redirect('shop_home')

def _get_business_context(request):
    """Helper to get basic business info for the template (Logo, Name)"""
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain: return {}
    
    supabase = get_supabase_client()
    try:
        res = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
        if res.data:
            biz = res.data[0]
            # Normalize components to find the theme
            components_raw = biz.get('components', [])
            
            if isinstance(components_raw, str):
                try: components_raw = json.loads(components_raw)
                except: components_raw = []
            
            # Find the WebTheme component and normalize all components
            components_list = []
            for c in components_raw:
                if isinstance(c, dict):
                    components_list.append(normalize_component_data(c))
            
            theme_comp = next((c for c in components_list if c.get('clean_type') == 'webtheme'), None)
            
            biz['components'] = components_list
            biz['theme_component'] = theme_comp
            
            # DEBUG LOGGING
            try:
                with open('theme_debug.log', 'a') as f:
                    f.write(f"Business Context Theme: {theme_comp}\n")
            except: pass
            
            return biz
    except Exception as e:
        logger.error(f"Business Context Error: {e}")
        pass
    return {}

from django.urls import reverse
import os


def google_login_view(request):
    supabase = get_supabase_client()

    # Prefer an explicitly configured OAuth callback base (useful for production)
    # Example: OAUTH_CALLBACK_BASE=https://nexassearch.com
    oauth_base = os.getenv('OAUTH_CALLBACK_BASE')
    if oauth_base:
        # Include the original request origin as `next` so the central callback can return to the subdomain
        original_origin = f"{request.scheme}://{request.get_host()}"
        callback_url = oauth_base.rstrip('/') + reverse('auth_callback') + f"?next={original_origin}"
    else:
        # Fallback to the request host (good for local testing)
        callback_url = request.build_absolute_uri(reverse('auth_callback'))
    
    try:
        # Prepare OAuth options with proper redirect URL
        # Note: Make sure the value of `callback_url` is registered in your
        # Supabase project's OAuth redirect URIs (e.g. https://nexassearch.com/auth/callback)
        oauth_options = {
            "provider": "google",
            "options": {
                "redirectTo": callback_url,
                "skipBrowserRedirect": False,
                "scopes": "openid email profile"
            }
        }
        
        # Get OAuth URL from Supabase
        res = supabase.auth.sign_in_with_oauth(oauth_options)
        
        if res and hasattr(res, 'url') and res.url:
            logger.info(f"Google OAuth redirect initiated to: {res.url}")
            return redirect(res.url)
        else:
            logger.error(f"Invalid Supabase OAuth response: {res}")
            return render(request, 'storefront/login.html', {
                'error': 'Google login service temporarily unavailable. Please try email login.'
            })
            
    except AttributeError as e:
        logger.error(f"Supabase OAuth method error (check auth config): {e}")
        return render(request, 'storefront/login.html', {
            'error': 'OAuth configuration error. Please contact support or use email login.'
        })
    except Exception as e:
        logger.error(f"Google Login Error: {type(e).__name__}: {str(e)}", exc_info=True)
        return render(request, 'storefront/login.html', {
            'error': f'Google login failed. Please try again or use email login.'
        })


def auth_callback_view(request):
    return render(request, 'storefront/auth_callback.html')

def confirm_auth_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            access_token = data.get('access_token')
            
            supabase = get_supabase_client()
            # Verify user with Supabase using the token
            res = supabase.auth.get_user(access_token)
            
            if res.user:
                 logger.debug(f"Auth Success: Logged in user {res.user.email}")
                 request.session['user_id'] = res.user.id
                 request.session['user_email'] = res.user.email
                 return JsonResponse({'status': 'ok'})
            else:
                 logger.error("Auth Confirm: Supabase returned no user for token")
        except Exception as e:
            logger.error(f"Auth Confirm Error Trace: {e}", exc_info=True)
            
    return JsonResponse({'status': 'error', 'message': 'Authentication failed'}, status=400)
