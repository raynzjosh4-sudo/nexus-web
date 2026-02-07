# SEO Implementation Guide - Code Examples

## 1. Enhanced Business Schema (base.html)

Replace the current schema in `storefront/templates/storefront/base.html` with this improved version:

```html
<!-- Structured Data (JSON-LD) - ENHANCED -->
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "{{ business.business_name|default:'Nexus Shop' }}",
    "description": "{{ business.business_description|default:'Premium online shop' }}",
    "url": "{{ request.build_absolute_uri }}",
    "logo": "{{ business.logo_url|default:'' }}",
    {% if business.business_phone_number %}"telephone": "{{ business.business_phone_number }}",{% endif %}
    {% if business.business_address %}"address": {
        "@type": "PostalAddress",
        "streetAddress": "{{ business.business_address|default:'' }}",
        "addressCountry": "{{ business.address_country|default:'UG' }}"
    },{% endif %}
    "image": "{{ business.logo_url|default:'' }}",
    "priceRange": "{{ business.price_range|default:'$$' }}",
    "sameAs": [
        {% if business.facebook_url %}"{{ business.facebook_url }}",{% endif %}
        {% if business.instagram_url %}"{{ business.instagram_url }}",{% endif %}
        {% if business.twitter_url %}"{{ business.twitter_url }}"{% endif %}
    ],
    "foundingDate": "{{ business.founded_date|default:'' }}",
    "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "Customer service",
        "telephone": "{{ business.business_phone_number|default:'' }}",
        "email": "{{ business.business_email|default:'' }}"
    }
}
</script>

<!-- Canonical URL (prevents duplicate content) -->
<link rel="canonical" href="{{ request.build_absolute_uri }}" />

<!-- Breadcrumb Structured Data (for business pages) -->
{% if breadcrumb %}
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
            "name": "{{ business.business_name }}",
            "item": "{{ request.build_absolute_uri }}"
        }
    ]
}
</script>
{% endif %}

<!-- Additional SEO Meta Tags -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
<meta name="author" content="{{ business.business_name|default:'Nexus' }}" />
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />

<!-- Preload critical business images -->
{% if business.logo_url %}
<link rel="preload" as="image" href="{{ business.logo_url }}" />
{% endif %}
```

---

## 2. Enhanced Product Schema (product_detail.html)

Replace product schema with this improved version:

```html
<!-- Product Schema - ENHANCED with aggregate rating and breadcrums -->
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "{{ product.name|default:'Product' }}",
    "description": "{{ product.description|truncatewords:50|striptags }}",
    "image": "{{ product.image_url }}",
    "sku": "{{ product.id }}",
    "url": "{{ request.build_absolute_uri }}",
    "brand": {
        "@type": "Brand",
        "name": "{{ business.business_name }}"
    },
    "offers": {
        "@type": "Offer",
        "price": "{{ product.price|floatformat:2 }}",
        "priceCurrency": "{{ product.currency|default:'UGX' }}",
        "availability": "https://schema.org/{% if product.in_stock %}InStock{% else %}OutOfStock{% endif %}",
        "url": "{{ request.build_absolute_uri }}",
        "seller": {
            "@type": "LocalBusiness",
            "name": "{{ business.business_name }}",
            "url": "https://{{ request.subdomain }}.nexassearch.com/",
            "logo": "{{ business.logo_url|default:'' }}"
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

<!-- Product Breadcrumb Schema -->
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
        },
        {% if product.category %}{
            "@type": "ListItem",
            "position": 2,
            "name": "{{ product.category }}",
            "item": "https://{{ request.subdomain }}.nexassearch.com/category/{{ product.category|lower|slugify }}/"
        },{% endif %}
        {
            "@type": "ListItem",
            "position": {% if product.category %}3{% else %}2{% endif %},
            "name": "{{ product.name }}",
            "item": "{{ request.build_absolute_uri }}"
        }
    ]
}
</script>

<!-- Canonical URL to prevent duplicate content -->
<link rel="canonical" href="{{ request.build_absolute_uri }}" />

<!-- Link to business page for SEO juice -->
<link rel="related" href="https://{{ request.subdomain }}.nexassearch.com/" title="{{ business.business_name }}" />
```

---

## 3. Enhanced robots.txt with Crawl Parameters

Update `storefront/views/robots.py`:

```python
def robots_txt(request):
    """Generate robots.txt with optimized crawl directives."""
    subdomain = getattr(request, 'subdomain', None)
    
    if subdomain:
        # Business subdomain - aggressive crawling for fresh content
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
Disallow: *?*sort=
Disallow: *?*page=
Disallow: /.env
Disallow: /media/uploads/temp/*

User-agent: Googlebot
Crawl-delay: 0
Request-rate: 100/1h

User-agent: *
Crawl-delay: 1

# Sitemap for search engines to discover content
Sitemap: https://{subdomain}.nexassearch.com/sitemap.xml
"""
    else:
        # Main domain - only Googlebot for sitemap index
        robots_content = """User-agent: *
Disallow: /

User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: *
Crawl-delay: 1

Sitemap: https://nexassearch.com/sitemap_index.xml
Sitemap: https://nexassearch.com/sitemap.xml
"""
    
    return HttpResponse(robots_content, content_type='text/plain')
```

---

## 4. Sitemap Enhancement (add product metadata)

Update `storefront/views/sitemap.py` to include more metadata:

```python
def sitemap_products(request):
    """Generate enhanced sitemap with images and lastmod."""
    subdomain = getattr(request, 'subdomain', None)
    
    if not subdomain:
        return HttpResponse("Sitemap not available", status=404)

    supabase = get_supabase_client()
    
    # Fetch business
    biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    if not biz_response.data:
        return HttpResponse("Business not found", status=404)
    
    business_id = biz_response.data[0].get('id')
    
    # Fetch all products with updated timestamps
    posts_response = supabase.table('posts')\
        .select('id,data,created_at,updated_at')\
        .eq('business_id', business_id)\
        .order('updated_at', desc=True)\
        .execute()
    
    urls = []
    
    # Add shop home with highest priority
    urls.append({
        'loc': request.build_absolute_uri('/'),
        'lastmod': datetime.now().isoformat(),
        'changefreq': 'weekly',
        'priority': '1.0',
        'images': [],
    })
    
    # Add products with image references
    for post in posts_response.data:
        post_data = post.get('data', {})
        product_url = request.build_absolute_uri(f'/product/{post["id"]}/')
        
        # Extract product images for sitemap
        images = []
        images_list = post_data.get('images', [])
        if images_list and isinstance(images_list, list):
            for img in images_list[:3]:  # Google recommends max 1000 images per URL, but limit to 3 per product
                img_url = img.get('url') if isinstance(img, dict) else str(img)
                if img_url:
                    images.append({
                        'loc': img_url,
                        'title': post_data.get('productName', 'Product Image'),
                    })
        
        urls.append({
            'loc': product_url,
            'lastmod': post.get('updated_at', post.get('created_at', datetime.now().isoformat())),
            'changefreq': 'weekly',
            'priority': '0.8',
            'images': images,
        })
    
    sitemap_xml = render_to_string('storefront/sitemap.xml', {'urls': urls})
    return HttpResponse(sitemap_xml, content_type='application/xml')
```

---

## 5. Sitemap XML Template with Images

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
        {% for image in url.images %}
        <image:image>
            <image:loc>{{ image.loc }}</image:loc>
            <image:title>{{ image.title }}</image:title>
        </image:image>
        {% endfor %}
    </url>
    {% endfor %}
</urlset>
```

---

## 6. Django View: Add Product Details Helper

Add to `storefront/views/product.py` to ensure proper data format for schema:

```python
def product_detail(request, product_id):
    """Enhanced product detail with SEO-optimized data."""
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        return redirect('http://localhost:8000')

    supabase = get_supabase_client()

    # Fetch business
    biz_response = supabase.table('business_profiles').select('*').eq('domain', subdomain).execute()
    if not biz_response.data:
        raise Http404("Shop not found")
    business_data = biz_response.data[0]
    
    # Fetch product
    posts_response = supabase.table('posts').select('*').eq('id', product_id).eq('business_id', business_data.get('id')).execute()
    if not posts_response.data:
        raise Http404("Product not found")
    
    post = posts_response.data[0]
    post_data = post.get('data', {})
    
    # Prepare product object with SEO fields
    product = {
        'id': post.get('id'),
        'name': post_data.get('productName', 'Untitled'),
        'description': post_data.get('textContent', ''),
        'price': float(post_data.get('productPrice', 0)),
        'currency': post_data.get('productCurrency', 'UGX'),
        'category': post_data.get('category', 'General'),
        'image_url': get_product_image(post_data),
        'in_stock': post_data.get('stock_status') != 'out_of_stock',
        'average_rating': post_data.get('reviews_avg'),
        'review_count': post_data.get('reviews_count'),
    }
    
    return render(request, 'storefront/partials/mainstore/product_detail.html', {
        'product': product,
        'business': normalize_business_data(business_data),
        'theme_component': get_theme_component(business_data),
    })

def get_product_image(post_data):
    """Get first available product image for SEO."""
    images = post_data.get('images', [])
    if images and isinstance(images, list) and len(images) > 0:
        first = images[0]
        return first.get('url') if isinstance(first, dict) else str(first)
    return post_data.get('thumbnailUrl') or post_data.get('imageUrl') or ''

def normalize_business_data(business_data):
    """Normalize business data for template with all SEO fields."""
    return {
        'id': business_data.get('id'),
        'business_name': business_data.get('business_name', 'Shop'),
        'business_description': business_data.get('business_description', ''),
        'business_phone_number': business_data.get('phone_number', ''),
        'business_email': business_data.get('email', ''),
        'business_address': business_data.get('address', ''),
        'address_country': business_data.get('country', 'UG'),
        'logo_url': business_data.get('logo_url', ''),
        'price_range': business_data.get('price_range', '$$'),
        'facebook_url': business_data.get('facebook_url', ''),
        'instagram_url': business_data.get('instagram_url', ''),
        'twitter_url': business_data.get('twitter_url', ''),
        'founded_date': business_data.get('founded_date', ''),
        'website_url': business_data.get('website_url', ''),
        'currency': business_data.get('currency', 'UGX'),
    }
```

---

## 7. Testing Your SEO Setup

### Test Canonical URLs
```bash
curl -i https://acme.nexassearch.com/product/<id>/ | grep -i canonical
# Should output: <link rel="canonical" href="https://acme.nexassearch.com/product/<id>/" />
```

### Test JSON-LD Schema
1. Go to https://schema.org/validator
2. Paste your product/business page URL
3. Verify "@type": "Product" or "@type": "LocalBusiness" appears

### Test Sitemap
```bash
curl https://acme.nexassearch.com/sitemap.xml | head -20
# Should show XML with <url> tags
```

### Test robots.txt
```bash
curl https://acme.nexassearch.com/robots.txt
# Should show crawling rules + Sitemap line
```

---

## 8. Database Fields Needed (Supabase)

Ensure `business_profiles` table has these fields for full SEO:

```sql
-- Add to business_profiles if missing
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS business_phone_number TEXT;
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS business_email TEXT;
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS business_address TEXT;
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'UG';
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS facebook_url TEXT;
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS instagram_url TEXT;
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS twitter_url TEXT;
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS founded_date DATE;
ALTER TABLE business_profiles ADD COLUMN IF NOT EXISTS price_range TEXT DEFAULT '$$';
```

Ensure `posts` table has these fields for products:

```sql
-- Add to posts if missing
ALTER TABLE posts ADD COLUMN IF NOT EXISTS reviews_avg FLOAT;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS reviews_count INTEGER;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS stock_status TEXT DEFAULT 'in_stock';
```

---

## 9. Next Steps (In Priority Order)

1. **Update base.html** with enhanced LocalBusiness schema (10 min)
2. **Update product_detail.html** with enhanced Product schema (10 min)
3. **Submit sitemap to Google Search Console** (2 min)
4. **Monitor gsearch results** - check back in 1-2 weeks

Then after 2 weeks:
5. Add product reviews functionality + schema
6. Add breadcrumb navigation + schema
7. Optimize meta descriptions per business

