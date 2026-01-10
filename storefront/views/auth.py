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
            # Authenticate with Supabase
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if res.user:
                # Store session data
                request.session['user_id'] = res.user.id
                request.session['user_email'] = res.user.email
                # We can store token if we want to make authenticated calls on behalf of user
                # request.session['access_token'] = res.session.access_token
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('shop_home') # Ensure this name exists in urls.py
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
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
            # 1. Sign up with Supabase Auth
            res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "display_name": name
                        # We can add more metadata here
                    }
                }
            })
            
            # 2. Check result
            if res.user:
                # If email confirmation is disabled or auto-confirmed:
                if res.session:
                     # Log them in immediately
                    request.session['user_id'] = res.user.id
                    request.session['user_email'] = res.user.email
                    logger.info(f"Signup Success: {email}")
                    return redirect('shop_home')
                else:
                    # If email confirmation is required, Supabase returns user but no session
                    # For this use case, we might want to just tell them to check email, 
                    # OR if the project config allows it, they are logged in.
                    # Assuming we want auto-login, we need the session. 
                    # If we don't get a session, we redirect to login with a message.
                    return render(request, 'storefront/login.html', {
                        'error': "Account created! Please check your email to confirm registration.",
                        'business': _get_business_context(request)
                    })
            else:
                 # Should theoretically throw exception if fail, but just in case
                return render(request, 'storefront/signup.html', {
                    'error': "Signup failed. Please try again.",
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

def google_login_view(request):
    supabase = get_supabase_client()
    callback_url = request.build_absolute_uri(reverse('auth_callback'))
    
    try:
        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirectTo": callback_url
            }
        })
        if res.url:
            return redirect(res.url)
    except Exception as e:
        logger.error(f"Google Login Error: {e}")
        
    return redirect('login')

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
