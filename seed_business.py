import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storefront.models import BusinessProfile

def create_business():
    # Check if exists
    if BusinessProfile.objects.filter(domain='shoe').exists():
        print("Business 'shoe' already exists.")
        return

    # Data matching the visual description/schema
    BusinessProfile.objects.create(
        business_name="Nexus Businesses",
        domain="shoe", # Default subdomain assumed in views
        business_description="Innovating for the Future",
        category="Premium Quality Sleep Essentials",
        logo_url="https://via.placeholder.com/150", # Placeholder for now
        # Using a reliable image for the cover
        components='[{"type":"ProfileWebsiteThemeComponent","primaryColor":"#f97316","backgroundColor":"#121418","surfaceColor":"#181b21","textColor":"#ffffff"}]',
        status='verified'
    )
    print("Created 'Nexus Businesses' profile.")

if __name__ == "__main__":
    create_business()
