# 🎯 SEO Implementation Checklist - What To Do Next

## Your Goal
Make businesses and products appear in Google search when people search for them.

---

## PHASE 1: IMMEDIATE (This Week) ⚡

### Task 1: Verify Sitemaps Work
Time: 5 minutes

```bash
# 1. Test in PowerShell
curl https://acme.nexassearch.com/sitemap.xml

# Should show XML with <url> tags for products
# If error: Check `.env` has SUPABASE_URL and SUPABASE_KEY

# 2. Test robots.txt
curl https://acme.nexassearch.com/robots.txt

# Should show crawling rules and: "Sitemap: https://acme.nexassearch.com/sitemap.xml"
```

**If works:** ✅ Skip to Task 2
**If not:** ❌ Check SUPABASE credentials in `.env` file

---

### Task 2: Copy Code Snippets Into Templates
Time: 15 minutes

**Step 1: Update base.html**
1. Open: `storefront/templates/storefront/base.html`
2. Find: `<head>` section (around line 5)
3. Add: Content from **SEO_CODE_SNIPPETS.md → SNIPPET 1** (after existing meta tags)
4. Save file

**Step 2: Update product_detail.html**
1. Open: `storefront/templates/storefront/partials/mainstore/product_detail.html`
2. Find: `<head>` section (around line 5)
3. Replace: Entire `<head>...</head>` with content from **SEO_CODE_SNIPPETS.md → SNIPPET 2**
4. Save file

**Step 3: Update sitemap.xml template**
1. Open: `storefront/templates/storefront/sitemap.xml`
2. Replace: Entire file with **SEO_CODE_SNIPPETS.md → SNIPPET 3**
3. Save file

**Step 4: Update sitemap_index.xml template**
1. Open: `storefront/templates/storefront/sitemap_index.xml`
2. Replace: Entire file with **SEO_CODE_SNIPPETS.md → SNIPPET 4**
3. Save file

**Step 5: Update views/robots.py**
1. Open: `storefront/views/robots.py`
2. Replace: Entire file with **SEO_CODE_SNIPPETS.md → SNIPPET 5**
3. Save file

**Step 6: Update views/sitemap.py**
1. Open: `storefront/views/sitemap.py`
2. Replace: `sitemap_products()` function with **SEO_CODE_SNIPPETS.md → SNIPPET 6**
3. Save file

**Step 7: Update views/sitemap_index.py**
1. Open: `storefront/views/sitemap_index.py`
2. Replace: Entire file with **SEO_CODE_SNIPPETS.md → SNIPPET 7**
3. Save file

---

### Task 3: Verify Changes Work
Time: 5 minutes

```bash
# 1. Test sitemap still generates
curl https://acme.nexassearch.com/sitemap.xml | head -20
# Should show: <?xml version="1.0" encoding="UTF-8"?>

# 2. Test product page loads
curl https://acme.nexassearch.com/product/<any-product-id>/ | head -100
# Should show HTML with Product schema in <head>

# 3. Check for errors in Django logs (if running server)
# Should see no 500 errors
```

**All working?** ✅ Proceed to Phase 2
**Errors?** ❌ Check file syntax or contact support

---

## PHASE 2: SUBMISSION (Mid-Week) 🚀

### Task 1: Create Google Search Console Account
Time: 5 minutes

1. Go to: https://search.google.com/search-console
2. Sign in with your Google account
3. Click: **"Add Property"**

---

### Task 2: Add Property #1 - Main Domain
Time: 3 minutes

1. Property type: **URL prefix**
2. Enter: `https://nexassearch.com`
3. Click: **Continue**
4. Verify ownership: Use recommended DNS method or HTML file upload
5. Submit sitemaps:
   - Go to: **Sitemaps** section (left menu)
   - Enter: `https://nexassearch.com/sitemap_index.xml`
   - Click: **Submit**

---

### Task 3: Add Property #2 - Business Template (Wildcard)
Time: 5 minutes

1. Click: **Add Property** again
2. Property type: **URL prefix**
3. Enter: `https://acme.nexassearch.com` (use one real business as template)
4. Verify ownership
5. Submit sitemaps:
   - Go to: **Sitemaps** section
   - Enter: `https://acme.nexassearch.com/sitemap.xml`
   - Click: **Submit**

🎉 **Your sitemaps are now submitted!**

---

## PHASE 3: MONITORING (After 1 Week) 📊

### Task 1: Check Coverage Report
Time: 5 minutes

In Google Search Console:
1. Property: `https://acme.nexassearch.com`
2. Left menu: **Coverage** (under "Indexing")
3. Look for:
   - ✅ "Home" page indexed
   - ✅ "Products" indexed (check count)
   - ❌ Errors or warnings (fix if any)

**Expected:** All pages should show "Indexed"

---

### Task 2: Check Performance
Time: 5 minutes

In Google Search Console:
1. Left menu: **Performance** (under "Discover")
2. Look at:
   - **Impressions** (how many times your pages appeared in search)
   - **Clicks** (how many people clicked)
   - **Position** (average ranking - want < 20)

**Expected:** After 2-4 weeks, you should see:
- 5-10 impressions per week
- 0-2 clicks per week  
- Improving rankings over time

---

### Task 3: Check for Indexing Issues
Time: 5 minutes

1. Left menu: **Coverage**
2. Check tabs:
   - **Valid** - ✅ Good, pages are indexed
   - **Valid with warnings** - ⚠️ Review, might need fixes
   - **Excluded** - ❌ Pages Google skipped (check `robots.txt`)
   - **Error** - ❌ Broken pages (check URLs)

**Action:** If many pages are "Excluded" or "Error", check:
- `robots.txt` - Is it blocking crawlers?
- `sitemap.xml` - Are URLs correct?
- Business/product data in Supabase

---

## PHASE 4: OPTIMIZATION (After 2-4 Weeks) 🎯

Once you see impressions in Google Search Console:

### Task 1: Improve Click-Through Rate
Goal: Get people to click your links in search results

What affects CTR:
1. **Title** (from `<title>` tag)
   - Should include business name OR product name
   - Should be descriptive (not generic)
   - Max 60 characters

2. **Meta Description** (from `<meta name="description">`)
   - 120-160 characters
   - Should tell user what they'll find
   - Include relevant keywords

**Action:** Update your business and product templates to have better titles/descriptions:

```html
<!-- For business page: -->
<title>{{ business.business_name }} - Shop Premium Products | Nexus</title>
<meta name="description" content="{{ business.business_description|truncatewords:15 }}" />

<!-- For product page: -->
<title>{{ product.name }} - Buy at {{ business.business_name }}</title>
<meta name="description" content="{{ product.description|truncatewords:20 }}" />
```

---

### Task 2: Add Internal Links
Goal: Help Google understand your site structure

Add these links:
- Each product page → links back to business homepage
- Business homepage → featured products
- Products by category

HTML example (add to templates):
```html
<!-- On product page, show "Shop at Business ABC" -->
<a href="https://{{ request.subdomain }}.nexassearch.com/">
    Shop at {{ business.business_name }}
</a>

<!-- On business page, show featured products -->
<a href="https://{{ request.subdomain }}.nexassearch.com/product/{{ product.id }}/">
    {{ product.name }}
</a>
```

---

### Task 3: Encourage Reviews
Goal: Higher ratings = higher click-through rate

What to implement:
- Add review system to products
- Show star ratings in search results
- Include in Product schema: `"aggregateRating": {"ratingValue": "4.5", "reviewCount": "120"}`

This makes your search result look like:
```
⭐⭐⭐⭐⭐ (120 reviews)
Product Name - $50,000 UGX
```

---

## PHASE 5: GROWTH (Month 2+) 📈

### Task 1: Monitor Rankings
Track which keywords bring traffic:

1. Google Search Console → **Performance**
2. Filter by: **Queries** that get clicks
3. Note: Keywords that rank 11-20 (potential to improve)

Example:
```
Query               Impressions  Clicks  Position
─────────────────   ───────────  ──────  ────────
Alice Shop          45           3       18       ← Can improve
Blue Shirt Alice    12           1       25       ← Can improve
Premium Fashion     8            0       31       ← Too low
```

---

### Task 2: Improve High-Potential Keywords
For keywords ranking 11-20:

1. **Improve content:** Make description more compelling
2. **Build backlinks:** Get other sites to link to you (social media, influencers)
3. **Improve CTR:** Better title/description (Phase 4 Task 1)

---

### Task 3: Expand to More Businesses
Once one business ranks well:

1. Verify other businesses are in sitemap index
2. Submit their sitemaps to Google Search Console
3. Repeat optimization for each

---

## Database Updates Needed (Optional but Recommended)

To support enhanced SEO, add these fields to Supabase:

```sql
-- For business_profiles table:
ALTER TABLE business_profiles 
ADD COLUMN IF NOT EXISTS business_phone_number TEXT,
ADD COLUMN IF NOT EXISTS business_email TEXT,
ADD COLUMN IF NOT EXISTS business_address TEXT,
ADD COLUMN IF NOT EXISTS facebook_url TEXT,
ADD COLUMN IF NOT EXISTS instagram_url TEXT,
ADD COLUMN IF NOT EXISTS twitter_url TEXT;

-- For posts table:
ALTER TABLE posts
ADD COLUMN IF NOT EXISTS reviews_count INTEGER,
ADD COLUMN IF NOT EXISTS reviews_avg FLOAT;
```

This allows schema to show:
- Business contact info
- Social media links  
- Product ratings/reviews

---

## Success Metrics

After 4-8 weeks, you should see:

| Metric | Expected | Timeline |
|--------|----------|----------|
| Pages indexed | 90%+ | Week 2 |
| Search impressions | 10+ per week | Week 3 |
| Click-through rate | 2-5% | Week 4 |
| Top 20 rankings | 3-5 keywords | Week 6 |
| Top 10 rankings | 1-2 keywords | Week 8+ |

---

## Troubleshooting

### Problem: "Pages not indexed"
**Check:**
1. `robots.txt` - Is it blocking crawlers? (`Disallow: /` on main domain is correct)
2. `sitemap.xml` - Are URLs correct? Test with curl
3. Site errors - Check Google Search Console "Coverage" report

**Fix:**
```python
# In robots.py, ensure business sitemaps are pointed:
Sitemap: https://{subdomain}.nexassearch.com/sitemap.xml
```

---

### Problem: "0 impressions after 2 weeks"
**Usually means:** Google hasn't crawled yet

**Solutions:**
1. **Request indexing manually:** Google Search Console → URL Inspection → "Request Indexing"
2. **Check robots.txt:** Make sure you're not blocking Google
3. **Build backlinks:** Share on social media (tells Google your site exists)

---

### Problem: "Schema markup shows errors"
**Validate schema:**
1. Go to: https://schema.org/validator
2. Paste product URL
3. Fix errors shown

**Common issues:**
- Missing fields: `price`, `priceCurrency`
- Wrong data type: `"price": "50000"` should be number, not string
- Broken URLs in schema

---

## Quick Links

- **Google Search Console:** https://search.google.com/search-console
- **Schema Validator:** https://schema.org/validator  
- **PageSpeed Insights:** https://pagespeed.web.dev/
- **Mobile-Friendly Test:** https://search.google.com/test/mobile-friendly
- **Google Search Gallery:** https://www.google.com/webmasters/markup-helper/

---

## Estimated Timeline

- **Phase 1 (Today):** 30 minutes
- **Phase 2 (Day 2-3):** 20 minutes
- **Phase 3 (After 1 week):** Review metrics
- **Phase 4 (After 2-4 weeks):** Start optimization
- **Phase 5 (Month 2+):** Expansion & growth

**Total effort:** ~2 hours setup + 30 min/week monitoring = Free, permanent customer discovery 🎉

