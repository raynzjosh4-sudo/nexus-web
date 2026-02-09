# Nexus Web Codebase - AI Agent Instructions

## Project Overview
**Nexus Web** is a Django 6.0 multi-tenant SaaS storefront platform. Each business (`business_profiles` table) gets a branded shop via subdomain (e.g., `alice.nexassearch.com`). Products are stored as `posts` with JSON `data` field. Backend is Supabase (PostgreSQL + realtime). UI rendered server-side using Django templates + component mapping system.

## Architecture at a Glance

### Request Flow
```
HTTP Request → SubdomainMiddleware (extracts 'alice' from 'alice.localhost')
  → Django URL Router (storefront/urls.py)
    → View handler (shop.py, product.py, etc)
      → Supabase fetch (SELECT * FROM business_profiles WHERE domain='alice')
        → normalize_component_data() → type mapping → template resolution
          → Django template render → HTML response
```

### Multi-Tenant Model
- **No subdomain** → redirect to main domain (JS frontend or public homepage)
- **With subdomain** → serve that business's shop with its profile components and products
- **Key distinction**: `request.subdomain` extracted by `SubdomainMiddleware` in `core/middleware.py`
- **Business data shape**: `{id, domain, business_name, components: [...], logo_url, status, ...}`
- **Product data shape**: `{id, business_id, data: {productName, productPrice, images: [{url}], ...}, created_at}`

## Critical Patterns & Conventions

### 1. Component Type Normalization (Essential Pattern)
Components from Supabase may have inconsistent type names (database has `"ProfileServicesComponent"`, template expects `"servicelist"`). The `normalize_component_data()` function in `storefront/views/shop.py` maps these:

```python
type_mapping = {
    'services': 'servicelist',        # DB: "ProfileServicesComponent" → "services" → "servicelist"
    'features': 'featurelist',         # DB: "ProfileFeaturesComponent" → "features" → "featurelist"
    'downloads': 'filedownload',       # DB: "ProfileDownloadsComponent" → "downloads" → "filedownload"
    'tabs': 'tabbedcontent',           # DB: "ProfileTabsComponent" → "tabs" → "tabbedcontent"
    # Add new types here when adding new component templates
}
```

**Pattern**: Always call `normalize_component_data(raw_component)` before rendering. The function returns `{'clean_type': 'servicelist', ...}`.

**If a component type doesn't render**: 1) Check database raw type, 2) Add entry to `type_mapping` dict, 3) Ensure template exists at `storefront/templates/storefront/components/{clean_type}.html`.

### 2. Component Rendering (Template-Based)
Components render via isolated templates in `storefront/templates/storefront/components/`:
- Pass as context dict: `render_to_string('storefront/components/hero.html', {'component': comp})`
- Each template receives the full component dict - use `{{ component.fieldName }}` to access
- **Fallback logic**: If no template found, `render_legacy_component()` handles old product description types

### 3. Subdomain Routing & Multi-Tenant Access
`core/middleware.py` extracts subdomain via hostname parsing:
- `alice.nexassearch.com` → `request.subdomain = 'alice'`
- `loom.localhost:8000` → `request.subdomain = 'loom'` (if `ALLOW_LOCALHOST_SUBDOMAINS=True`)
- Bare `nexassearch.com` → `request.subdomain = None` (redirects to JS frontend)

**Usage in views**: `subdomain = request.subdomain` then fetch: `supabase.table('business_profiles').eq('domain', subdomain).select('*')`

### 4. Sitemap Generation (SEO Critical)
Multi-part workflow for search engine indexing:
- **`sitemap_index.py`** - Discovers all published businesses → generates `sitemap_index.xml`
- **`sitemap.py`** - Per-business sitemap with product URLs + image refs (called per request)
- **`sitemap_static.py`** - Pregenerated sitemaps stored in `storefront/static/sitemaps/` (via `run_sitemap_generation.py`)
- **`robots.py`** - Serves `robots.txt` with Sitemap-Index location

**Pattern**: Use `run_sitemap_generation.py` script to pregenerate all static sitemaps periodically (daily via cron or Windows Task Scheduler). Dynamic fallback in views if static cache is stale.

### 5. Data Structure Safety
**Always use `.get()` with defaults** for nested data (especially `post['data']` dict):

```python
post_data = post.get('data', {})  # Handle missing 'data'
product_name = post_data.get('productName', 'Untitled')
images = post_data.get('images', [])
```

Components may be JSON strings or lists - validate type: `components = json.loads(components) if isinstance(components, str) else components`

## Environment & Configuration

### `.env` Variables (required)
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SECRET_KEY=your-django-secret
DEBUG=True  # or False
ALLOWED_HOSTS=.nexassearch.com,.localhost,localhost,127.0.0.1
ALLOW_LOCALHOST_SUBDOMAINS=True  # Allow alice.localhost for local dev
```

### Django Settings Overrides
- `DEBUG` - read from env
- `ALLOWED_HOSTS` - multi-tenant friendly (wildcard subdomains)
- `DATABASES` - SQLite for dev or PostgreSQL for production
- `ALLOW_LOCALHOST_SUBDOMAINS` - enables `alice.localhost` routing in dev mode

## Common Tasks & Quick Commands

### Run Dev Server
```bash
python manage.py runserver 0.0.0.0:8000
# Visit: http://alice.localhost:8000/ (with ALLOW_LOCALHOST_SUBDOMAINS=True)
```

### Regenerate All Sitemaps
```bash
python run_sitemap_generation.py
# Creates/updates XML files in storefront/static/sitemaps/
```

### Check Business Status
```bash
python check_business_status.py
# Shows active/inactive business distribution, useful for SEO debugging
```

### Database (SQLite or PostgreSQL)
```bash
python manage.py migrate
python manage.py shell
```

### Direct Component Testing
```python
from storefront.views.shop import normalize_component_data
from storefront.utils.component_renderer import render_single_component

# Test normalization
comp = {'type': 'ProfileServicesComponent', 'title': 'Services'}
normalized = normalize_component_data(comp)
html = render_single_component(normalized)
print(html)
```

## Testing & Debugging Tips

### Check Subdomain Extraction
Request a URL like `http://alice.localhost:8000/` and inspect:
```python
print(request.subdomain)  # should be 'alice'
print(request.full_host)  # should be 'alice.localhost'
```

### Debug Component Rendering
Use the component normalizer directly:
```python
from storefront.views.shop import normalize_component_data
normalized = normalize_component_data(raw_component)
print(normalized.get('clean_type'))  # check mapped type
```

### Check Business Status & Sitemaps
Quick diagnostic scripts available:
- `check_business_status.py` - Shows all businesses, their status distribution (active/inactive/pending)
- `run_sitemap_generation.py` - Regenerates all static sitemaps for published businesses
- `validate_production_sitemaps.py` - Validates sitemap XML structure and URLs are crawlable

Run in Django shell:
```bash
python manage.py shell
>>> from storefront.client import get_supabase_client
>>> supabase = get_supabase_client()
>>> biz = supabase.table('business_profiles').eq('domain', 'alice').select('*').execute()
>>> print(biz.data[0] if biz.data else 'Not found')
```

### Common Error Sources
- **Missing component template** → check `storefront/templates/storefront/components/` for file match
- **Sitemaps not updating** → run `python run_sitemap_generation.py` to refresh static cache
- **Images not showing** → inspect `post['data']['images']` structure (might be list of dicts or list of URLs)
- **Component not rendering** → ensure type is in `type_mapping` dict and template exists

## Known Quirks & Gotchas

1. **Components as JSON strings** - Business components may be stored as JSON strings, not lists. Always parse: `json.loads(components_raw) if isinstance(components_raw, str) else components_raw`

2. **Image field order** - Products can have images in multiple places: `post_data['images']`, `post_data['thumbnailUrl']`, `post_data['imageUrl']`. Check in order and fallback gracefully.

3. **Type name inconsistencies** - A component might be `ProfileTestimonialComponent`, `testimonial`, or `testimonials`. The `type_mapping` dict in `normalize_component_data()` handles this, but always test with real Supabase data.

4. **Subdomain localhost support** - Localhost subdomains only work if `ALLOW_LOCALHOST_SUBDOMAINS=True` in settings.

5. **CORS for forms** - Cross-subdomain forms require proper CORS setup and `CSRF_TRUSTED_ORIGINS` config.

6. **Status field filtering** - Business profiles have a `status` field (active/inactive/pending). Sitemaps only include "active" businesses. Check this when businesses don't appear in search results.

7. **Component type mapping is case-insensitive** - The normalize function converts to lowercase, so `ProfileServicesComponent`, `services`, and `servicelist` all map to `servicelist` template.

## Key Supabase Tables
- `business_profiles` - Store business data, components, metadata
- `posts` - Store products/content
- `categories` - Product categories
- `auth.users` - User authentication

Query pattern: `supabase.table(table_name).select(columns).eq(field, value).execute()`

## Routing & URL Structure

### URL Patterns (from `storefront/urls.py`)
- `/` - Shop homepage
- `/product/<product_id>/` - Product detail view
- `/profile/<business_id>/` - Business profile view (if public)
- `/category/<category_slug>/` - Products filtered by category
- `/sitemap.xml` - Business-specific product sitemap
- `/sitemap_index.xml` - Master sitemap index for all businesses
- `/robots.txt` - Search engine directives

### View Files
- **`shop.py`** - `shop_home()`, `index()`, `normalize_component_data()`
- **`product.py`** - Product detail rendering, image handling
- **`profile.py`** - Business profile pages
- **`sitemap.py`**, **`sitemap_static.py`**, **`sitemap_index.py`** - SEO sitemaps
- **`robots.py`** - `robots.txt` generation
- **`auth.py`** - Login, signup, auth callbacks
- **`order.py`** - Order processing
- **`wishlist.py`** - Wishlist functionality

## Code Style & Patterns
- Use `logger = logging.getLogger(__name__)` for debugging
- Exception handling: log, then render fallback HTML or raise Http404
- Template context: always include `business` dict for navbar/footer
- View naming: `{action}_view` (e.g., `product_detail`, `login_view`)
- Import organization: Django → local modules → third-party
- Safe data extraction: Always use `.get(key, default_value)` for nested dicts
- Type checking: `isinstance(value, list)` or `isinstance(value, str)` before processing

## Implementation Details (Discovered Patterns)

### Middleware Subdomain Extraction
The `SubdomainMiddleware` in `core/middleware.py` handles:
1. **Primary domain** (`nexassearch.com`) - strips to extract subdomain
2. **Localhost development** - `alice.localhost` extracts `alice` (if `ALLOW_LOCALHOST_SUBDOMAINS=True`)
3. **Generic fallback** - multi-label hosts like `shop.test.local` extract first parts as subdomain

**Never assume subdomain exists** - always check `request.subdomain is not None` before accessing.

### Component Normalization Flow
```
Raw component from DB → normalize_component_data()
  ↓
Strip 'Profile' and 'Component' prefixes, lowercase
  ↓
Look up in type_mapping dict (e.g., 'services' → 'servicelist')
  ↓
Return {'clean_type': 'servicelist', ...}
  ↓
render_single_component() looks up template:
  'servicelist' → 'storefront/components/services.html'
  ↓
If template found, render with component dict as context
If not found, fallback to render_legacy_component()
```

### Legacy Component Handling
Old product descriptions may have types like:
- `TextComponent` → renders as `<p>` tags
- `RichTextComponent` → renders as `<div>` with HTML content
- Unknown types → logged as warning, empty string returned

Check `render_legacy_component()` in `component_renderer.py` for fallback behavior.

## Search Engine Visibility (SEO/SEM)

Each business storefront and product page must be discoverable by Google. The indexing flow:
1. **Sitemaps** (`sitemap_index.xml` → individual `sitemap.xml`) - Tell Google what to crawl
2. **robots.txt** - Point to sitemaps, disallow sensitive pages (login, order confirmation)
3. **Schema Markup** - JSON-LD in `<head>` tells Google page type (LocalBusiness for shops, Product for items)
4. **Meta Tags** - Title, description, Open Graph (social sharing), canonical URLs

**Key files:**
- `storefront/views/robots.py` - Generates robots.txt with sitemap links
- `storefront/views/sitemap.py` - Generates per-business product sitemaps
- `storefront/views/sitemap_index.py` - Discovers all published businesses
- `storefront/templates/storefront/base.html` - LocalBusiness schema + meta tags
- `storefront/templates/storefront/partials/mainstore/product_detail.html` - Product schema + OG tags

**Critical pattern:** NEVER drop meta tags or schema markup—they're how Google indexes your content.

## Files to Not Touch Without Care
- `core/settings.py` - Multi-tenant config is fragile (subdomain domains, CORS, cookies)
- `core/middleware.py` - Subdomain extraction logic is mission-critical
- `storefront/utils/component_renderer.py` - Component type mapping must stay in sync with templates
