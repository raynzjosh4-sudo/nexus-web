# Nexus Web - SEO & Schema Implementation Guide

**Last Updated**: March 10, 2026  
**Status**: ✅ Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Changes Made](#changes-made)
3. [JSON-LD Store Schema](#json-ld-store-schema)
4. [Data Mapping](#data-mapping)
5. [Fallback Values](#fallback-values)
6. [Google Knowledge Graph](#google-knowledge-graph)
7. [Implementation Details](#implementation-details)
8. [Testing & Validation](#testing--validation)

---

## Overview

This document outlines the SEO optimization and structured data implementation for Nexus Web. The goal is to make each business shop (storefront) visible to Google Search as a legitimate local business with proper schema markup.

### Why This Matters

- **Google Search Rankings**: Schema markup helps Google understand your business better
- **Knowledge Graph**: Rich snippets appear in search results with business details
- **Local Maps**: Geo coordinates enable local business searches
- **Shopping Features**: Product schema works alongside the business schema

---

## Changes Made

### 1. Fixed Login Prompt Component

**File**: `storefront/templates/storefront/partials/login_prompt.html`

**Issue**: CSS template syntax was broken with misplaced braces and line breaks inside style declarations.

**Solution**: Refactored to use CSS custom properties (`:root` variables) with proper Django template syntax:

```css
:root {
    --primary-bg: {% if theme_component %}{{ theme_component.surfaceColor|default:"#181b21" }}{% else %}#181b21{% endif %};
    --primary-text: {% if theme_component %}{{ theme_component.textColor|default:"#ffffff" }}{% else %}#ffffff{% endif %};
    --secondary-text: {% if theme_component %}{{ theme_component.secondaryTextColor|default:"#9ca3af" }}{% else %}#9ca3af{% endif %};
    --accent-color: {% if theme_component %}{{ theme_component.accentColor|default:"#f97316" }}{% else %}#f97316{% endif %};
}
```

**Benefits**:
- Theme variables evaluated once at page render
- Clean separation of template logic from CSS
- No broken output in browser DevTools
- Fallback colors always present

---

### 2. Added JSON-LD Store Schema

**File**: `storefront/templates/storefront/shop_home.html`

**Location**: `<head>` section, after theme CSS, before closing `</head>`

**Type**: Schema.org Store (Local Business)

The schema includes:

- **Business Identification**: Name, URL, Logo, Image
- **Contact**: Telephone numbers
- **Location**: Physical address with geo coordinates
- **Hours**: Opening hours (with fallback to 24/7)
- **Currency & Payment**: Price range, accepted currencies, payment methods
- **Service Area**: Geographic coverage (Uganda)
- **Social Links**: Facebook, Instagram, WhatsApp

---

## JSON-LD Store Schema

### Full Schema Structure

```json
{
    "@context": "https://schema.org",
    "@type": "Store",
    "@id": "https://{{ domain }}#store",
    "name": "{{ business_name }}",
    "url": "https://{{ domain }}/",
    "logo": "{{ logo_url }}",
    "image": ["{{ cover_image_url }}"],
    "description": "{{ business_description }}",
    "telephone": ["+256...", "+256...", "+256..."],
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "{{ business_address }}",
        "addressLocality": "Kampala",
        "addressRegion": "Central",
        "addressCountry": "UG"
    },
    "geo": {
        "@type": "GeoCoordinates",
        "latitude": "{{ latitude }}",
        "longitude": "{{ longitude }}"
    },
    "openingHoursSpecification": [
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "opens": "00:00",
            "closes": "23:59"
        }
    ],
    "priceRange": "{{ price_range }}",
    "currenciesAccepted": "UGX",
    "paymentAccepted": "Cash, Mobile Money, Credit Card",
    "areaServed": "Uganda",
    "sameAs": ["https://facebook.com", "https://instagram.com", "https://wa.me/..."]
}
```

---

## Data Mapping

| JSON-LD Property | Database Column | Source | Notes |
|---|---|---|---|
| `name` | `business_name` | `business_profiles` | Required - business name |
| `url` | `domain` | `request.META.HTTP_HOST` | Constructed as `https://{{ domain }}/` |
| `logo` | `logo_url` | `business_profiles` | Business profile logo |
| `image` | `cover_small_url` | `business_profiles` | Cover image for visual Knowledge Graph |
| `description` | `business_description` | `business_profiles` | Business bio/tagline |
| `telephone` | Default list | Hardcoded | Fallback numbers: Nexus support |
| `streetAddress` | `business_address` | `business_profiles` | Optional - fallback to "Church House Building..." |
| `latitude` | `latitude` | `business_profiles` | Optional - fallback to Kampala `0.3136` |
| `longitude` | `longitude` | `business_profiles` | Optional - fallback to Kampala `32.5812` |
| `priceRange` | `price_range` | `business_profiles` | Optional - defaults to `$$` |
| `areaServed` | Fixed to "Uganda" | Hardcoded | Multi-region support possible in future |

---

## Fallback Values

The schema gracefully handles missing data using Django template default filters:

```django
{{ business.business_name|default:'Nexus Shop' }}
{{ business.logo_url|default:'https://nexassearch.com/logo.png' }}
{{ business.cover_small_url|default:'https://nexassearch.com/default-cover.jpg' }}
{{ business.business_description|default:'Premium products and services...' }}
{{ business.price_range|default:'$$' }}
```

### Hardcoded Values (by design)

These are intentionally hardcoded because all Nexus businesses operate similarly:

```python
telephone: [
    "+256746010410",
    "+256790915604",
    "+256703590034"
]

address: {
    addressLocality: "Kampala",
    addressRegion: "Central",
    addressCountry: "UG"
}

openingHoursSpecification: {
    dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    opens: "00:00",
    closes: "23:59"
}

currenciesAccepted: "UGX"
paymentAccepted: "Cash, Mobile Money, Credit Card"
areaServed: "Uganda"
```

---

## Google Knowledge Graph

### What is it?

The Knowledge Graph is the information panel that appears on the right side of Google Search results when searching for a business.

### How It Works with Our Schema

1. **Business Identity**: The `@type: Store` and unique `@id` help Google identify this as a distinct business entity
2. **Logo & Image**: The `logo` and `image` properties populate the visual elements
3. **Contact Info**: Phone number and address in the knowledge panel
4. **Ratings* Ready**: Schema structure supports product ratings (implemented via separate Product schema)

### Example Knowledge Graph Result

```
┌─────────────────────────┐
│  CRIS NET               │
│  [Logo] [Cover Image]   │
│  Store • Kampala, UG    │
│  📞 +256 746 010 410    │
│  🌐 cris.nexassearch.com│
│  High quality nets...   │
│  Hours: Always Open     │
└─────────────────────────┘
```

---

## Implementation Details

### Template Location

**File**: `storefront/templates/storefront/shop_home.html`

**Position in HTML**:

```html
<head>
    ...
    <link rel="stylesheet" href="...">
    
    <style>
        :root { ... }
    </style>

    {# JSON-LD Store Schema for Google Search and Local Business #}
    <script type="application/ld+json">
    { "@context": "https://schema.org", ... }
    </script>
</head>
```

### Why in `<head>`?

- Google bots parse `<head>` before rendering the page
- Schema validation tools look for structured data in `<head>`
- Best practice for JSON-LD placement

### Request Context

The schema uses `request.META.HTTP_HOST` to dynamically detect the business domain:

```django
"@id": "https://{{ request.META.HTTP_HOST }}#store",
"url": "https://{{ request.META.HTTP_HOST }}/",
```

This works for:
- `alice.nexassearch.com` ✅
- `alice.localhost:8000` ✅ (dev)
- `alice.onrender.com` ✅ (preview)

---

## Testing & Validation

### 1. Google Rich Results Test

**URL**: https://search.google.com/test/rich-results

**Steps**:
1. Paste your shop URL (e.g., `https://cris.nexassearch.com/`)
2. Google will fetch and test for structured data
3. Check if "Store" schema is recognized ✅

**Expected Output**:
```
Valid structured data found:
- Schema.org Store (1)
  - name
  - url
  - logo
  - image
  - telephone
  - address
  - geo
  - openingHoursSpecification
```

### 2. Schema.org Validator

**URL**: https://validator.schema.org/

**Steps**:
1. Enter your shop URL
2. Validate the JSON-LD structure
3. Check for errors and warnings

**Common Issues & Fixes**:
- Missing required fields: Add fallback defaults ✅ (Done)
- Invalid date format: ISO 8601 format for times ✅ (Done)
- Geo coordinates: Must be valid lat/long ✅ (Done with fallbacks)

### 3. Local Testing

Use browser DevTools to verify schema is rendered:

```javascript
// Open DevTools > Console and run:
const scripts = document.querySelectorAll('script[type="application/ld+json"]');
console.log(JSON.parse(scripts[0].innerHTML));

// Output:
{
  "@context": "https://schema.org",
  "@type": "Store",
  "name": "CRIS NET",
  ...
}
```

### 4. Lighthouse Audit

**Steps**:
1. Open DevTools > Lighthouse
2. Run audit on your shop page
3. Check "SEO" section for schema markup validation

---

## SEO Impact Timeline

### Immediate (0-1 days)
- ✅ Schema is on page and valid
- ✅ Google bots can parse business info
- ✅ Rich Results Test passes

### Short-term (1-7 days)
- Google crawls and indexes schema
- Knowledge Graph panel may appear in search
- Product rich snippets start showing

### Medium-term (1-4 weeks)
- Business gains local search visibility
- "Near me" searches may include your shop
- Improved CTR from enriched search results

### Long-term (1+ months)
- Cumulative ranking boost for business keywords
- Higher conversion from qualified local traffic
- Business reputation and reviews accumulate

---

## Maintenance & Updates

### When to Update Schema

Update the schema when:
- ✏️ Business name changes
- 📷 Logo or cover image changes
- 📝 Business description updates
- 📍 Location or coordinates change
- 🏪 Hours of operation change
- 💰 Price range changes

### How It's Updated

Since we use Django template variables, schema updates automatically when:
1. Business profile is updated in Supabase
2. Page is re-rendered or cache cleared
3. No code changes needed!

---

## Complementary Schemas

The Store schema works alongside other schemas on Nexus:

### Product Schema
```json
{
  "@type": "Product",
  "name": "Round Net",
  "price": "35000",
  "priceCurrency": "UGX",
  "currencyConverted": "~$9.50",
  "seller": {
    "@type": "Store",
    "@id": "https://cris.nexassearch.com/#store"
  }
}
```

### BreadcrumbList Schema
```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "position": 1, "name": "Home", "item": "https://cris.nexassearch.com/" },
    { "position": 2, "name": "Products", "item": "https://cris.nexassearch.com/#view-products" }
  ]
}
```

---

## Common Questions

### Q: Why are phone numbers hardcoded?
**A**: All Nexus businesses share the same support/contact infrastructure. Individual businesses can add their own numbers via the database later if needed. Currently, the hardcoded numbers ensure all shops have valid contact info for the Knowledge Graph.

### Q: What if a business doesn't have coordinates?
**A**: We fall back to Kampala's general coordinates (`0.3136, 32.5812`). This is acceptable for now, but businesses can add their own coordinates to the database for more precise local search results.

### Q: Does this affect mobile search?
**A**: Yes! Google uses this schema for:
- Mobile "Near me" searches ✅
- Local business cards in maps ✅
- Mobile search results rich snippets ✅

### Q: How often does Google re-index schema?
**A**: Google crawls and re-evaluates schema on page refresh. Updates can be visible in Google Search Console within 24-48 hours, but organic ranking impact takes longer (1-4 weeks).

### Q: Can I test this locally?
**A**: Yes! Use Google Rich Results Test with your `localhost` URL. If ALLOW_LOCALHOST_SUBDOMAINS is enabled, Google can access it.

---

## Related Files

- **Schema Definition**: `storefront/templates/storefront/shop_home.html` (lines after theme CSS)
- **Database Schema**: `business_profiles` table columns (name, description, address, coordinates, etc.)
- **View Handler**: `storefront/views/shop.py` (passes business context to template)
- **Product Schema**: Implemented separately in product detail pages

---

## Next Steps

### Phase 2 Improvements (Future)

1. **Dynamic Coordinates**: Add optional `latitude`, `longitude` fields to business admin
2. **Custom Hours**: Allow business to set their own opening hours
3. **Ratings Schema**: Aggregate customer reviews for 5-star display
4. **Multiple Languages**: Add `inLanguage` property for multilingual schema
5. **Social Verification**: Add `foundingDate`, `founder` for trusted business indicators
6. **Video Schema**: Embed product videos in schema for richer search results

### Phase 3: Advanced SEO

1. **Organization Schema**: Nest business info inside Organization schema for corporate entities
2. **Event Schema**: Add events/promotions as structured data
3. **FAQPage Schema**: FAQ section structured for featured snippets
4. **HowTo Schema**: Step-by-step product guides in schema format

---

## Checklist for Deployment

- [x] JSON-LD schema added to shop_home.html
- [x] All required properties included with fallbacks
- [x] Hardcoded values set strategically (phone, address base, hours)
- [x] Database fields mapped correctly
- [x] Template syntax validated
- [x] Schema validates in Rich Results Test
- [x] Mobile responsiveness not affected
- [x] Performance impact minimal (static JSON in head)
- [x] Documentation complete
- [x] Ready for production deployment ✅

---

## Support & Debugging

### If Schema Doesn't Appear

1. **Check source code**: View > Source in browser, search for `application/ld+json`
2. **Validate JSON**: Paste schema into https://jsonlint.com/
3. **Test with Google**: Use https://search.google.com/test/rich-results
4. **Check console**: Look for JavaScript errors in DevTools
5. **Verify template rendering**: Ensure business context is passed to template

### If Google Doesn't Index

1. Wait 24-48 hours (initial crawl)
2. Submit URL to Google Search Console
3. Use URL Inspection tool to force re-crawl
4. Monitor "Coverage" > "Indexed" in Search Console

---

**Document Version**: 1.0  
**Last Reviewed**: March 10, 2026  
**Maintained By**: Nexus Development Team
