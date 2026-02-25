from django.shortcuts import render, redirect
from ..forms import ContactForm, SupportForm
from ..models import ContactSubmission, SupportTicket


def newsletter_view(request):
    return render(request, 'storefront/pages/newsletter.html')


def blog_view(request):
    return render(request, 'storefront/pages/blog.html')


def about_view(request):
    return render(request, 'storefront/pages/about.html')


def contact_view(request):
    """Standalone Contact page not tied to a business subdomain."""
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactSubmission.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            success = True
    else:
        form = ContactForm()

    return render(request, 'storefront/pages/contact.html', {'form': form, 'success': success})


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
