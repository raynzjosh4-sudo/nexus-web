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
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            return render(request, 'storefront/login.html', {
                'error': 'Email and password are required.',
                'business': _get_business_context(request)
            })
        
        supabase = get_supabase_client()
        
        try:
            # Authenticate with Supabase (handle multiple response shapes)
            logger.info(f"🔐 Login attempt for: {email}")
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})

            # Debug log the raw response for easier troubleshooting
            logger.info(f'📝 Sign-in response type: {type(res)}')
            logger.info(f'📝 Sign-in response: {getattr(res, "__dict__", res)}')

            user = None
            access_token = None

            # Try several common response shapes
            if hasattr(res, 'user') and res.user:
                user = res.user
                logger.info(f"✓ User found in res.user: {user}")
            elif isinstance(res, dict):
                # supabase-py may return dict with 'data' or 'user'
                user = res.get('user') or (res.get('data') and res['data'].get('user'))
                # Access token might be nested
                access_token = res.get('access_token') or (res.get('data') and res['data'].get('access_token'))
                logger.info(f"✓ User from dict: {user}")
            elif getattr(res, 'data', None):
                # Some SDKs expose a .data property
                data = res.data
                if isinstance(data, dict):
                    user = data.get('user')
                    access_token = data.get('access_token')
                logger.info(f"✓ User from res.data: {user}")
            else:
                logger.warning(f"⚠️ Could not extract user from response")

            if user:
                # Store session data
                # Handle both dict and User object responses from Supabase
                if isinstance(user, dict):
                    uid = user.get('id')
                    uemail = user.get('email')
                else:
                    # User object from supabase-py SDK
                    uid = getattr(user, 'id', None)
                    uemail = getattr(user, 'email', None)
                
                logger.info(f"📧 Extracted: uid={uid}, uemail={uemail}")
                
                request.session['user_id'] = uid
                request.session['user_email'] = uemail
                if access_token:
                    request.session['access_token'] = access_token
                
                logger.info(f"✅ Login successful for {uemail}, session saved, redirecting to shop_home")

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('shop_home')
            else:
                logger.error(f"❌ Login failed: No user in response")
                return render(request, 'storefront/login.html', {
                    'error': "Invalid email or password.",
                    'business': _get_business_context(request)
                })

        except Exception as e:
            logger.exception(f"❌ Login exception: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {str(e)}")
            error_msg = "Login error. Please check your credentials and try again."
            if "Invalid login credentials" in str(e):
                error_msg = "Invalid email or password."
            return render(request, 'storefront/login.html', {
                'error': error_msg,
                'business': _get_business_context(request)
            })
            
    return render(request, 'storefront/login.html', {
        'business': _get_business_context(request)
    })

def signup_view(request):
    subdomain = getattr(request, 'subdomain', None)
    
    if request.method == 'POST':
        # Validate and sanitize inputs
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = (request.POST.get('password') or '').strip()
        confirm_password = (request.POST.get('confirm_password') or '').strip()
        
        if not name or not email or not password:
            return render(request, 'storefront/signup.html', {
                'error': "All fields are required.",
                'business': _get_business_context(request)
            })
        
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
    if not subdomain: 
        return {}
    
    try:
        supabase = get_supabase_client()
        res = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
        
        if res.data and len(res.data) > 0:
            biz = res.data[0]
            
            # Safely handle components
            try:
                components_raw = biz.get('components', [])
                
                if isinstance(components_raw, str):
                    try: 
                        components_raw = json.loads(components_raw)
                    except: 
                        components_raw = []
                
                if not isinstance(components_raw, list):
                    components_raw = []
                
                # Find the WebTheme component and normalize all components
                components_list = []
                for c in components_raw:
                    if isinstance(c, dict):
                        try:
                            normalized = normalize_component_data(c)
                            if normalized:
                                components_list.append(normalized)
                        except Exception as comp_err:
                            logger.warning(f"Failed to normalize component: {comp_err}")
                            continue
                
                theme_comp = next((c for c in components_list if c.get('clean_type') == 'webtheme'), None)
                
                biz['components'] = components_list
                biz['theme_component'] = theme_comp or {}
                
            except Exception as theme_err:
                logger.warning(f"Error processing business theme: {theme_err}")
                biz['components'] = []
                biz['theme_component'] = {}
            
            return biz
    
    except Exception as e:
        logger.warning(f"Business Context Error (non-critical): {e}")
    
    return {}

from django.urls import reverse
import os


def google_login_view(request):
    supabase = get_supabase_client()

    # Build the callback URL based on environment and request
    # IMPORTANT: This must match a URL registered in Supabase OAuth settings
    oauth_callback_base = os.getenv('OAUTH_CALLBACK_BASE')
    
    if oauth_callback_base:
        # Production: Use configured base URL
        callback_url = oauth_callback_base.rstrip('/') + '/auth/callback/'
    else:
        # Local development: Build from request, but handle localhost subdomains
        # For localhost, we strip the subdomain to use the base localhost
        host = request.get_host()  # e.g., "alice.localhost:8000" or "localhost:8000" or "example.com"
        
        # Check if it's localhost with subdomain - we need to use localhost without subdomain for OAuth
        if 'localhost' in host and '.' in host:
            # Replace "alice.localhost:8000" with "localhost:8000" for OAuth callback
            parts = host.split('.')
            base_host = '.'.join(parts[-2:])  # Get last 2 parts: "localhost:8000"
            callback_url = f"{request.scheme}://{base_host}/auth/callback/"
        else:
            # Regular hostname - use as is
            callback_url = request.build_absolute_uri(reverse('auth_callback'))
    
    try:
        # Prepare OAuth options with proper redirect URL
        # Note: Make sure the value of `callback_url` is registered in your
        # Supabase project's OAuth redirect URIs
        oauth_options = {
            "provider": "google",
            "options": {
                "redirectTo": callback_url,
                "skipBrowserRedirect": False,
                "scopes": "openid email profile"
            }
        }
        
        logger.info(f"Google OAuth: Using callback URL: {callback_url}")
        
        # Get OAuth URL from Supabase
        res = supabase.auth.sign_in_with_oauth(oauth_options)
        
        if res and hasattr(res, 'url') and res.url:
            logger.info(f"Google OAuth redirect initiated to: {res.url}")
            return redirect(res.url)
        else:
            logger.error(f"Invalid Supabase OAuth response: {res}")
            return render(request, 'storefront/login.html', {
                'error': 'Google login service temporarily unavailable. Please try email login.',
                'business': _get_business_context(request)
            })
            
    except AttributeError as e:
        logger.error(f"Supabase OAuth method error (check auth config): {e}")
        return render(request, 'storefront/login.html', {
            'error': 'OAuth configuration error. Please contact support or use email login.',
            'business': _get_business_context(request)
        })
    except Exception as e:
        logger.error(f"Google Login Error: {type(e).__name__}: {str(e)}", exc_info=True)
        return render(request, 'storefront/login.html', {
            'error': 'Google login failed. Please try again or use email login.',
            'business': _get_business_context(request)
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
