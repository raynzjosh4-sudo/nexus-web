from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
import logging

from ..forms import ContactForm, SupportForm
from ..models import SupportTicket
from ..client import get_supabase_client

logger = logging.getLogger(__name__)


def newsletter_view(request):
    return render(request, 'storefront/pages/newsletter.html')


def blog_view(request):
    return render(request, 'storefront/pages/blog.html')


def about_view(request):
    return render(request, 'storefront/pages/about.html')


def contact_view(request):
    """Standalone Contact page. Sends message to business owner via email."""
    success = False
    error = None
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Get business owner email from subdomain
                supabase = get_supabase_client()
                subdomain = request.subdomain
                
                if subdomain:
                    # Fetch business profile to get owner email
                    business_data = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
                    
                    if business_data.data:
                        business = business_data.data[0]
                        owner_email = business.get('email') or business.get('contact_email')
                        business_name = business.get('business_name', 'Your Business')
                        
                        if owner_email:
                            # Prepare email
                            subject = f"New Contact Form Submission - {form.cleaned_data['name']}"
                            message = f"""
New contact form submission:

Name: {form.cleaned_data['name']}
Email: {form.cleaned_data['email']}
Message:
{form.cleaned_data['message']}
                            """
                            
                            # Send email to business owner
                            send_mail(
                                subject=subject,
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[owner_email],
                                fail_silently=False,
                            )
                            
                            success = True
                        else:
                            error = "Business email not configured. Please try again later."
                            logger.error(f"No email found for business '{subdomain}'")
                    else:
                        error = "Business not found. Please try again later."
                        logger.error(f"Business '{subdomain}' not found in Supabase")
                else:
                    # No subdomain - send to admin/default email
                    admin_emails = [email for name, email in settings.ADMINS] if hasattr(settings, 'ADMINS') and settings.ADMINS else [settings.DEFAULT_FROM_EMAIL]
                    
                    if admin_emails:
                        subject = f"New Contact Form Submission - {form.cleaned_data['name']}"
                        message = f"""
New contact form submission:

Name: {form.cleaned_data['name']}
Email: {form.cleaned_data['email']}
Message:
{form.cleaned_data['message']}
                        """
                        
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=admin_emails,
                            fail_silently=False,
                        )
                        
                        success = True
                    else:
                        error = "Unable to process your message. Please try again later."
                        logger.error("No admin emails configured and no business subdomain found")
                        
            except Exception as e:
                error = "An error occurred while processing your message. Please try again later."
                logger.exception(f"Error sending contact form email: {str(e)}")
    else:
        form = ContactForm()

    return render(request, 'storefront/pages/contact.html', {
        'form': form, 
        'success': success,
        'error': error
    })


def cookie_policy_view(request):
    return render(request, 'storefront/pages/cookie_policy.html')


def support_view(request):
    success = False
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            SupportTicket.objects.create(
                subject=form.cleaned_data['subject'],
                description=form.cleaned_data['description'],
                priority=form.cleaned_data['priority']
            )
            success = True
    else:
        form = SupportForm()

    return render(request, 'storefront/pages/support.html', {'form': form, 'success': success})


def join_business_view(request):
    return render(request, 'storefront/pages/join_business.html')
