from django.shortcuts import render
from django.http import Http404
from ..client import get_supabase_client


def contact(request):
    """
    Display business contact information.
    Fetches business details (phone, address, website, hours) from Supabase.
    """
    subdomain = getattr(request, 'subdomain', None)
    
    # If no subdomain, redirect to home or error page
    if not subdomain:
        raise Http404("No business specified.")
    
    supabase = get_supabase_client()
    
    # Fetch business profile
    response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    
    if not response.data:
        raise Http404(f"Business '{subdomain}' not found.")
    
    business = response.data[0]
    
    # Extract contact details from business profile
    contact_info = {
        'business_name': business.get('business_name', 'Contact'),
        'business_description': business.get('business_description', ''),
        'phone_number': business.get('business_phone_number'),
        'address': business.get('business_address'),
        'website': business.get('website_url'),
        'email': business.get('email'),  # Check if this field exists
        'latitude': business.get('latitude'),
        'longitude': business.get('longitude'),
        'opening_hours': business.get('opening_hours'),  # JSON field
        'logo_url': business.get('logo_url'),
        'place_name': business.get('place_name'),
    }
    
    # Parse opening hours if it's a JSON string
    opening_hours = contact_info.get('opening_hours')
    if opening_hours and isinstance(opening_hours, str):
        import json
        try:
            contact_info['opening_hours'] = json.loads(opening_hours)
        except:
            contact_info['opening_hours'] = None
    
    context = {
        'business': business,
        'contact_info': contact_info,
    }
    
    return render(request, 'storefront/contact.html', context)
