# Ready-to-Use Code Snippets - Copy & Paste Into Your Templates

## SNIPPET 1: Enhanced Business Page (base.html)

Add this to the `<head>` section of `storefront/templates/storefront/base.html`:

```html
{% comment %} SEO & Schema Markup for Business Pages {% endcomment %}

<!-- Canonical URL (prevents duplicate content) -->
<link rel="canonical" href="{{ request.build_absolute_uri }}" />

<!-- Business LocalBusiness Schema (JSON-LD) -->
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "{{ business.business_name|default:'Shop' }}",
    "description": "{{ business.business_description|default:'Premium online shopping' }}",
    "url": "{{ request.build_absolute_uri }}",
    "logo": "{{ business.logo_url|default:'' }}",
    "image": "{{ business.logo_url|default:'' }}",
    {% if business.business_phone_number %}"telephone": "{{ business.business_phone_number }}",{% endif %}
    {% if business.business_email %}"email": "{{ business.business_email }}",{% endif %}
    {% if business.business_address %}"address": {
        "@type": "PostalAddress",
        "streetAddress": "{{ business.business_address|default:'' }}",
        "addressCountry": "UG"
    },{% endif %}
    "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "Customer Service",
        {% if business.business_phone_number %}"telephone": "{{ business.business_phone_number }}"{% endif %}
    }
}
</script>

<!-- Breadcrumb Schema (helps Google understand site structure) -->
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": "https://nexassearch.com/"
        },
        {
            "@type": "ListItem",
            "position": 2,
            "name": "{{ business.business_name|default:'Shop' }}",
            "item": "{{ request.build_absolute_uri }}"
        }
    ]
}
</script>

<!-- Enhanced Meta Tags -->
<meta name="description" content="{{ business.business_description|default:'Shop premium products online'|truncatewords:20 }}" />
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
<meta property="og:type" content="business.business" />
<meta property="og:site_name" content="{{ business.business_name|default:'Nexus' }}" />
```

---

## SNIPPET 2: Enhanced Product Page (product_detail.html)

Replace the `<script type="application/ld+json">` and meta tags in `storefront/templates/storefront/partials/mainstore/product_detail.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Title & Description -->
    <title>{{ product.name }} - Buy at {{ business.business_name }} | Nexus Shop</title>
    <meta name="description" content="{{ product.description|truncatewords:20|striptags }}" />
    <meta name="keywords" content="{{ product.name }}, {{ product.category|default:'shopping' }}, {{ business.business_name }}" />
    <meta name="author" content="{{ business.business_name }}" />
    <meta name="robots" content="index, follow, max-image-preview:large" />
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{{ request.build_absolute_uri }}" />
    
    <!-- Open Graph (Social Media Preview) -->
    <meta property="og:type" content="product" />
    <meta property="og:title" content="{{ product.name }} - {{ business.business_name }}" />
    <meta property="og:description" content="{{ product.description|truncatewords:20|striptags }}" />
    <meta property="og:image" content="{{ product.image_url }}" />
    <meta property="og:url" content="{{ request.build_absolute_uri }}" />
    <meta property="og:site_name" content="{{ business.business_name }}" />
    {% if product.price %}<meta property="og:price:amount" content="{{ product.price|floatformat:2 }}" />{% endif %}
    {% if product.currency %}<meta property="og:price:currency" content="{{ product.currency }}" />{% endif %}
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{{ product.name }}" />
    <meta name="twitter:description" content="{{ product.description|truncatewords:15|striptags }}" />
    <meta name="twitter:image" content="{{ product.image_url }}" />
    
    <!-- Product Schema (JSON-LD) -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "{{ product.name|escapejs }}",
        "description": "{{ product.description|truncatewords:50|striptags|escapejs }}",
        "image": "{{ product.image_url|escapejs }}",
        "sku": "{{ product.id|escapejs }}",
        "url": "{{ request.build_absolute_uri|escapejs }}",
        "brand": {
            "@type": "Brand",
            "name": "{{ business.business_name|escapejs }}"
        },
        "offers": {
            "@type": "Offer",
            "price": "{{ product.price|floatformat:2 }}",
            "priceCurrency": "{{ product.currency|default:'UGX' }}",
            "availability": "https://schema.org/{% if product.in_stock %}InStock{% else %}OutOfStock{% endif %}",
            "url": "{{ request.build_absolute_uri|escapejs }}",
            "seller": {
                "@type": "Organization",
                "name": "{{ business.business_name|escapejs }}",
                "url": "https://{{ request.subdomain }}.nexassearch.com/"
            }
        }
        {% if product.average_rating and product.review_count %},
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "{{ product.average_rating|floatformat:1 }}",
            "reviewCount": "{{ product.review_count }}",
            "bestRating": "5",
            "worstRating": "1"
        }
        {% endif %}
    }
    </script>
    
    <!-- Breadcrumb List Schema -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://{{ request.subdomain }}.nexassearch.com/"
            }
            {% if product.category %},
            {
                "@type": "ListItem",
                "position": 2,
                "name": "{{ product.category|escapejs }}",
                "item": "https://{{ request.subdomain }}.nexassearch.com/category/{{ product.category|lower|slugify }}/"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": "{{ product.name|escapejs }}",
                "item": "{{ request.build_absolute_uri|escapejs }}"
            }
            {% else %}
            ,
            {
                "@type": "ListItem",
                "position": 2,
                "name": "{{ product.name|escapejs }}",
                "item": "{{ request.build_absolute_uri|escapejs }}"
            }
            {% endif %}
        ]
    }
    </script>
</head>
```

---

## SNIPPET 3: Sitemap XML Template (sitemap.xml)

Update `storefront/templates/storefront/sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
    {% for url in urls %}
    <url>
        <loc>{{ url.loc }}</loc>
        {% if url.lastmod %}<lastmod>{{ url.lastmod|slice:":10" }}</lastmod>{% endif %}
        {% if url.changefreq %}<changefreq>{{ url.changefreq }}</changefreq>{% endif %}
        {% if url.priority %}<priority>{{ url.priority }}</priority>{% endif %}
        
        {# Include product images for Google Image Search #}
        {% for image in url.images %}
        <image:image>
            <image:loc>{{ image.loc|escapejsstring }}</image:loc>
            <image:title>{{ image.title|escapejsstring }}</image:title>
        </image:image>
        {% endfor %}
    </url>
    {% endfor %}
</urlset>
```

---

## SNIPPET 4: Sitemap Index Template (sitemap_index.xml)

Update `storefront/templates/storefront/sitemap_index.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {% for sitemap in sitemaps %}
    <sitemap>
        <loc>{{ sitemap.loc }}</loc>
        <lastmod>{{ sitemap.lastmod|default:now|date:"Y-m-d" }}</lastmod>
    </sitemap>
    {% endfor %}
</sitemapindex>
```

---

## SNIPPET 5: robots.txt View

Update `storefront/views/robots.py`:

```python
from django.http import HttpResponse


def robots_txt(request):
    """Generate robots.txt with SEO-optimized crawl directives."""
    subdomain = getattr(request, 'subdomain', None)
    
    if subdomain:
        # Business subdomain - allow search engines to crawl products
        robots_content = f"""User-agent: *
Allow: /
Allow: /product/
Allow: /category/
Disallow: /admin/
Disallow: /login/
Disallow: /signup/
Disallow: /logout/
Disallow: /auth/
Disallow: */order/*
Disallow: */checkout/*
Disallow: /.env
Disallow: /media/uploads/temp/*

User-agent: Googlebot
Crawl-delay: 0
Request-rate: 100/1h

User-agent: Bingbot
Crawl-delay: 1
Request-rate: 30/1h

User-agent: *
Crawl-delay: 1

Sitemap: https://{subdomain}.nexassearch.com/sitemap.xml
"""
    else:
        # Main domain - direct search engines to sitemap index
        robots_content = """User-agent: *
Allow: /robots.txt
Allow: /sitemap*
Disallow: /

User-agent: Googlebot
Allow: /
Crawl-delay: 0

Sitemap: https://nexassearch.com/sitemap_index.xml
"""
    
    return HttpResponse(robots_content, content_type='text/plain')
```

---

## SNIPPET 6: Enhanced Sitemap View

Update `storefront/views/sitemap.py`:

```python
import json
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from ..client import get_supabase_client
from datetime import datetime
from urllib.parse import urljoin


logger = logging.getLogger(__name__)


def sitemap_products(request):
    """Generate sitemap for products with image references."""
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        return HttpResponse("Sitemap not available", status=404)

    try:
        supabase = get_supabase_client()
        
        # Fetch business
        biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
        if not biz_response.data:
            return HttpResponse("Business not found", status=404)
        
        business_id = biz_response.data[0].get('id')
        
        # Fetch all products
        posts_response = supabase.table('posts')\
            .select('id,data,created_at,updated_at')\
            .eq('business_id', business_id)\
            .order('updated_at', desc=True)\
            .limit(50000)\
            .execute()
        
        urls = []
        
        # Add shop homepage first (highest priority)
        urls.append({
            'loc': request.build_absolute_uri('/'),
            'lastmod': datetime.now().isoformat(),
            'changefreq': 'weekly',
            'priority': '1.0',
            'images': [],
        })
        
        # Add products (check changefreq)
        for post in posts_response.data:
            post_data = post.get('data', {})
            product_url = request.build_absolute_uri(f'/product/{post["id"]}/')
            
            # Extract images for sitemap
            images = []
            images_list = post_data.get('images', [])
            if images_list and isinstance(images_list, list):
                for idx, img in enumerate(images_list[:3]):  # Max 3 images per product
                    img_url = img.get('url') if isinstance(img, dict) else str(img)
                    if img_url and img_url.startswith('http'):
                        images.append({
                            'loc': img_url,
                            'title': f"{post_data.get('productName', 'Product')} - Image {idx+1}",
                        })
            
            # Determine last modified date
            lastmod = post.get('updated_at') or post.get('created_at') or datetime.now().isoformat()
            
            urls.append({
                'loc': product_url,
                'lastmod': lastmod,
                'changefreq': 'weekly',
                'priority': '0.8',
                'images': images,
            })
        
        sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
        return HttpResponse(sitemap_xml, content_type='application/xml')
        
    except Exception as e:
        logger.exception(f"Sitemap generation error: {e}")
        return HttpResponse(f"Error generating sitemap: {str(e)}", status=500)
```

---

## SNIPPET 7: Sitemap Index View

Update `storefront/views/sitemap_index.py`:

```python
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from ..client import get_supabase_client
from datetime import datetime


logger = logging.getLogger(__name__)


def sitemap_index(request):
    """Generate sitemap index for all published business sitemaps."""
    try:
        supabase = get_supabase_client()
        
        # Fetch all published businesses with domains
        biz_response = supabase.table('business_profiles')\
            .select('domain,updated_at')\
            .eq('status', 'published')\
            .limit(50000)\
            .execute()
        
        sitemaps = []
        for biz in biz_response.data:
            if biz.get('domain'):
                sitemaps.append({
                    'loc': f"https://{biz['domain']}.nexassearch.com/sitemap.xml",
                    'lastmod': biz.get('updated_at', datetime.now().isoformat()),
                })
        
        logger.info(f"Sitemap index includes {len(sitemaps)} business sitemaps")
        sitemap_index_xml = render_to_string('storefront/sitemap_index.xml', {
            'sitemaps': sitemaps,
            'now': datetime.now(),
        })
        return HttpResponse(sitemap_index_xml, content_type='application/xml')
        
    except Exception as e:
        logger.exception(f"Sitemap index generation error: {e}")
        return HttpResponse(f"Error generating sitemap index: {str(e)}", status=500)
```

---

## SNIPPET 8: Helper: Normalize Business Data (views/product.py)

Add this function to extract important fields for templates:

```python
def normalize_business_data(business_data):
    """Prepare business data for SEO-optimized templates."""
    return {
        'id': business_data.get('id'),
        'domain': business_data.get('domain'),
        'business_name': business_data.get('business_name', 'Shop'),
        'business_description': business_data.get('business_description', ''),
        'business_phone_number': business_data.get('phone_number') or business_data.get('business_phone_number'),
        'business_email': business_data.get('email') or business_data.get('business_email'),
        'business_address': business_data.get('address') or business_data.get('business_address'),
        'logo_url': business_data.get('logo_url'),
        'website_url': business_data.get('website_url'),
        'currency': business_data.get('currency', 'UGX'),
        'facebook_url': business_data.get('facebook_url', ''),
        'instagram_url': business_data.get('instagram_url', ''),
        'twitter_url': business_data.get('twitter_url', ''),
    }
```

---

## Quick Installation Steps

1. **Update base.html** (business pages):
   - Find: `<head>` section
   - Add: SNIPPET 1 content

2. **Update product_detail.html** (product pages):
   - Find: `<head>` section
   - Replace: entire head section with SNIPPET 2

3. **Update sitemap.xml** template:
   - Replace: entire file with SNIPPET 3

4. **Update sitemap_index.xml** template:
   - Replace: entire file with SNIPPET 4

5. **Update robots.py**:
   - Replace: `def robots_txt()` with SNIPPET 5

6. **Update sitemap.py**:
   - Replace: `def sitemap_products()` with SNIPPET 6

7. **Update sitemap_index.py**:
   - Replace: `def sitemap_index()` with SNIPPET 7

8. **Test**:
   ```bash
   curl https://acme.nexassearch.com/robots.txt
   curl https://acme.nexassearch.com/sitemap.xml | head -20
   ```

---

## Verify Installation

```bash
# 1. Check sitemap generates correctly
curl -I https://acme.nexassearch.com/sitemap.xml
# Should return: HTTP/1.1 200 OK

# 2. Check product page has canonical URL
curl https://acme.nexassearch.com/product/<id>/ | grep canonical

# 3. Check robots.txt points to sitemap
curl https://acme.nexassearch.com/robots.txt | grep Sitemap

# 4. Validate JSON-LD schema
# Go to: https://schema.org/validator
# Paste: https://acme.nexassearch.com/product/<id>/
# Should show: "@type": "Product"
```

