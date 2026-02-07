# SEO & Search Indexing Strategy for Nexus Web Multi-Tenant Marketplace

## Overview: How Businesses & Products Appear in Google Search

Your marketplace needs to make **both businesses (storefronts) AND products searchable**. Here's the complete flow:

```
Google Bot crawls sitemap
    ↓
Finds business storefronts: https://acme.nexassearch.com/
Finds product pages: https://acme.nexassearch.com/product/<id>/
    ↓
Indexes pages using SEO metadata + structured data
    ↓
User searches for "Alice Shop" or "Blue Shirt"
    ↓
Google displays result with business name + description or product name + image
    ↓
User clicks → lands on business storefront or product page
```

---

## 1. SITEMAPS (Discovery & Indexing)

### Current Status
✅ **Implemented:** `sitemap.xml` (products), `sitemap_index.xml`, `robots.txt`

### How It Works

**For Main Domain (`nexassearch.com/sitemap_index.xml`):**
- Discovers all published businesses
- Points to individual business sitemaps

**For Each Business (`acme.nexassearch.com/sitemap.xml`):**
- Lists all products for that business
- Lists the shop homepage
- Includes `lastmod` and `changefreq` so Google knows what to re-crawl

### Submit to Google Search Console
1. Go to https://search.google.com/search-console
2. Add two properties:
   - **`https://nexassearch.com`** → Submit `https://nexassearch.com/sitemap_index.xml`
   - **`https://acme.nexassearch.com`** (template/wildcard) → Submit `https://acme.nexassearch.com/sitemap.xml`

---

## 2. STRUCTURED DATA (Schema Markup)

### Current Status
✅ **Partially implemented:**
- Base template has LocalBusiness schema for business pages
- Product page has Product schema
- ⚠️ **Need to add:** Price/availability in product schema, AggregateRating, review data

### How It Works
Schema markup tells Google what type of page it is:

**Business Pages** (e.g., `https://acme.nexassearch.com/`)
```jsonld
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Alice Shop",
  "url": "https://acme.nexassearch.com",
  "logo": "https://...",
  "address": {...},
  "description": "Alice's premium fashion store",
  "telephone": "+1234567890",  // if available
  "image": "https://...",
  "sameAs": ["https://facebook.com/Alice", ...]  // social profiles
}
```

**Product Pages** (e.g., `https://acme.nexassearch.com/product/<id>/`)
```jsonld
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Blue Casual Shirt",
  "description": "...",
  "image": "https://...",
  "sku": "<product-id>",
  "brand": {
    "@type": "Brand",
    "name": "Alice Shop"  // ← Links back to business
  },
  "offers": {
    "@type": "Offer",
    "price": "50000",
    "priceCurrency": "UGX",
    "availability": "https://schema.org/InStock",
    "url": "https://acme.nexassearch.com/product/<id>/",
    "seller": {
      "@type": "LocalBusiness",
      "name": "Alice Shop",
      "url": "https://acme.nexassearch.com"
    }
  },
  "aggregateRating": {  // Optional: if you have reviews
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "120"
  }
}
```

---

## 3. META TAGS (Search Preview & Social Sharing)

### Business Page (`base.html`)
```html
<title>{{ business.business_name }} - Premium Shop | Nexus</title>
<meta name="description" content="{{ business.business_description }}">
<meta name="keywords" content="{{ business.business_name }}, shopping, store">

<!-- Open Graph (Facebook, LinkedIn) -->
<meta property="og:type" content="business.business">
<meta property="og:title" content="{{ business.business_name }}">
<meta property="og:description" content="{{ business.business_description }}">
<meta property="og:image" content="{{ business.logo_url }}">
<meta property="og:url" content="{{ request.build_absolute_uri }}">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ business.business_name }}">
<meta name="twitter:image" content="{{ business.logo_url }}">
```

### Product Page (`product_detail.html`)
```html
<title>{{ product.name }} - Buy at {{ business.business_name }}</title>
<meta name="description" content="{{ product.description|truncatewords:20 }}">

<!-- Open Graph (shows product preview) -->
<meta property="og:type" content="product">
<meta property="og:image" content="{{ product.image_url }}">  <!-- Product image shows in Google Images & social -->
<meta property="og:price:amount" content="{{ product.price }}">
<meta property="og:price:currency" content="{{ product.currency }}">
```

---

## 4. ROBOTS.TXT (Crawling Rules)

### Current Status
✅ **Implemented** in `storefront/views/robots.py`

### What It Does
```
User-agent: *            # All search engines
Allow: /                 # Crawl homepage
Disallow: /admin/        # Don't crawl admin
Disallow: /login/        # Don't crawl auth pages
Disallow: */order/       # Don't crawl order confirmation
Sitemap: https://acme.nexassearch.com/sitemap.xml  # Tell Google where the sitemap is
```

**Good!** Your setup prevents crawling of sensitive pages while allowing product & business pages.

---

## 5. FINAL SEO CHECKLIST

### For Business Pages to Rank
- [ ] ✅ Unique business name (`<h1>`)
- [ ] ✅ Descriptive meta description (80-160 chars)
- [ ] ✅ Logo image (for rich snippet)
- [ ] ✅ LocalBusiness schema with business details
- [ ] ⚠️ **TODO:** Add `telephone` & `address` to schema (if available in DB)
- [ ] ⚠️ **TODO:** Add social media links (`sameAs`) if business has them

### For Products to Rank
- [ ] ✅ Unique product name (`<h1>`)
- [ ] ✅ Product image in `<meta property="og:image">`
- [ ] ✅ Price & currency in Product schema
- [ ] ✅ Availability status (InStock/OutOfStock)
- [ ] ⚠️ **TODO:** Handle reviews/ratings if you have them
- [ ] ⚠️ **TODO:** Add breadcrumb schema for category navigation

### For SEO Visibility
- [ ] ✅ Sitemaps submitted to Google Search Console
- [ ] ✅ robots.txt properly configured
- [ ] ✅ Mobile-responsive design
- [ ] ⚠️ **TODO:** Add internal links between business & products
- [ ] ⚠️ **TODO:** Add canonical URLs to prevent duplicate content

---

## 6. IMPLEMENTATION ROADMAP

### Phase 1: Submit to Search Engines
1. **Google Search Console** - Verify both `nexassearch.com` and wildcard domain
2. **Bing Webmaster Tools** - Submit sitemaps
3. **Monitor crawl errors** - Check for 404s on products

### Phase 2: Enhance Structured Data
1. **Update business schema** - Add telephone, address, social links
2. **Update product schema** - Add reviews if available
3. **Add breadcrumb schema** - Help Google understand category structure

### Phase 3: Optimize On-Page SEO
1. Each business creates profile with:
   - Business description (for meta tag)
   - Business category/type (e.g., "Fashion Boutique")
   - Contact info (phone, address)
   - Social media links
2. Each product has:
   - Clear product name (indexed as `<h1>`)
   - Detailed description (first 160 chars = Google snippet)
   - High-quality product image
   - Category assignment

### Phase 4: Technical SEO
1. Ensure all URLs are unique and permanent
2. Set up 301 redirects for any URL changes
3. Add internal linking (e.g., product → business shop)
4. Monitor Core Web Vitals (speed, layout shift, interactivity)

---

## 7. EXAMPLE: How A Search Result Appears

### User searches: "Alice Shop Blue Shirt"

**Google Result for Business:**
```
Alice Shop
acme.nexassearch.com
Your premium fashion destination. Discover exclusive blue casual shirts, ...
★★★★★ (if you have reviews)
```
← This comes from base.html meta description + schema

**Google Result for Product:**
```
Blue Casual Shirt - Buy at Alice Shop
acme.nexassearch.com/product/<id>/
50,000 UGX ✓ In Stock
Your favorite blue casual shirt with premium fabric, ...
🖼️ [Product image]
```
← This comes from product_detail.html meta + schema

When user clicks → Lands on your product page which displays the business info + product details + option to buy

---

## 8. MONITORING & IMPROVEMENTS

### Tools to Use
1. **Google Search Console** - See which pages rank, get impressions/clicks
2. **Google PageSpeed Insights** - Check performance score
3. **Lighthouse (Chrome DevTools)** - Audit SEO compliance
4. **Structured Data JSON-LD Validator** - Verify schema is correct

### Track Success
After 2-4 weeks of submission:
```
Goal: "Alice Shop" → should appear in search
Goal: "Blue Shirt Alice Shop" → product should rank
Metric: Track impressions in GSC to see if Google is finding you
```

---

## 9. PRIORITY FIXES (If You Want Max SEO Impact)

**Must-Have:**
- [x] Sitemaps working (you have this)
- [x] robots.txt allowing crawl (you have this)
- [x] Basic schema markup (you have this)
- [ ] **Add phone number & address to business schema** ← Do this first
- [ ] **Generate unique meta descriptions** from business.business_description

**Nice-to-Have:**
- [ ] Add review/rating schema if you track reviews
- [ ] Add breadcrumb navigation (category → product)
- [ ] Internal linking between related products
- [ ] FAQ schema for common questions

