# Nexus Web Codebase - AI Agent Instructions

## Project Overview
**Nexus Web** is a Django 6.0 multi-tenant SaaS storefront platform. Each business gets a branded shop accessible via subdomain (e.g., `acme.nexassearch.com`). Backend is Supabase (PostgreSQL auth + realtime database). Dynamic UI components are rendered server-side using Django templates.

## Architecture at a Glance

### Request Flow
```
HTTP Request → SubdomainMiddleware (extracts subdomain)
  → Django URL Router (storefront/urls.py)
    → View (e.g., shop_home in storefront/views/shop.py)
      → Supabase fetch (business_profiles, posts tables)
        → normalize_component_data() (type mapping)
          → render_component_list() → Django templates
            → HTML response
```

### Key Files by Responsibility
- **`core/settings.py`** - Django config, CORS setup, subdomain domain settings
- **`core/middleware.py`** - `SubdomainMiddleware`: parses host header, sets `request.subdomain`
- **`storefront/models.py`** - Django ORM models (Product, Category) - minimal use
- **`storefront/views/*.py`** - Request handlers (auth, shop, product, profile, etc.)
- **`storefront/client.py`** - Supabase client initialization from `.env`
- **`storefront/utils/component_renderer.py`** - Component type mapping + rendering logic
- **`storefront/templates/storefront/`** - Django templates (base.html, component templates)

## Critical Patterns & Conventions

### 1. Multi-Tenant via Subdomain
- **No subdomain** → redirect to main domain (JS frontend at localhost:5500 or nexassearch.com)
- **With subdomain** (e.g., `alice`) → serve the `alice` business's storefront
- Subdomain extracted by `SubdomainMiddleware` and available as `request.subdomain`
- Business data fetched from `business_profiles` table via: `supabase.table('business_profiles').select('*').eq('domain', subdomain)`

### 2. Component Normalization Pattern
Components from Supabase DB come with inconsistent type names (e.g., `ProfileServicesComponent`, `services`, `servicelist`). **Always normalize before rendering**:

```python
from storefront.utils.component_renderer import normalize_component_data
component = normalize_component_data(raw_component)
clean_type = component.get('clean_type')  # standardized type
```

Type mapping lives in `normalize_component_data()` in `component_renderer.py`. Patterns:
- `services` → `servicelist`
- `features` → `featurelist`
- `downloads` → `filedownload`
- `tabs` → `tabbedcontent`

**Missing a component type?** Add to the `type_mapping = {...}` dict.

### 3. Template Rendering
Components render via isolated Django templates in `storefront/templates/storefront/components/`:
- `hero.html`, `gallery.html`, `pricing.html`, etc.
- Pass component dict as context: `render_to_string('storefront/components/hero.html', {'component': comp})`
- Fallback: if no template found, `render_legacy_component()` handles legacy types (TextComponent, RichTextComponent, etc.)

### 4. Data Structure Patterns
**Business object** (from `business_profiles`):
```python
{
    'id': uuid,
    'domain': 'alice',  # subdomain
    'business_name': 'Alice Shop',
    'components': '[...]' or [...],  # JSON string or list
    'logo_url': 'https://...',
    ...
}
```

**Post object** (product):
```python
{
    'id': uuid,
    'business_id': uuid,
    'data': {  # ← Main content
        'productName': 'Shirt',
        'productPrice': 50,
        'productCurrency': 'UGX',
        'images': [{'url': '...'}, ...],
        'textContent': 'description',
        ...
    },
    'created_at': '2025-02-07...'
}
```

**Always safely extract nested data** — use `.get()` with defaults for missing fields.

### 5. Authentication
- Sign-in/up via Supabase auth (email/password or Google OAuth)
- Session stored in Django: `request.session['user_id']`, `request.session['user_email']`
- Access token (if needed): `request.session['access_token']`
- Handle multiple Supabase SDK response shapes (object attrs vs dict keys)

### 6. Error Handling Conventions
- **Missing component data** → return `f"<!-- Render Error: {e} -->"` for HTML, or graceful fallback
- **Missing shop** → raise `Http404(f"Shop '{subdomain}' not found.")`
- **Missing Supabase config** → check `.env` file for `SUPABASE_URL` and `SUPABASE_KEY`
- **Logging** → use `logger = logging.getLogger(__name__)` and log exceptions for debugging

## Environment & Configuration

### `.env` Variables (required)
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SECRET_KEY=your-django-secret
DEBUG=True  # or False
ALLOWED_HOSTS=.nexassearch.com,.localhost,localhost,127.0.0.1
```

### Django Settings Overrides
- `DEBUG` - read from env
- `ALLOWED_HOSTS` - multi-tenant friendly (wildcard subdomains)
- `DATABASES` - SQLite for dev
- `SESSION_COOKIE_DOMAIN` / `CSRF_COOKIE_DOMAIN` - `.nexassearch.com` for subdomain sharing

## Common Tasks & Quick Commands

### Run Dev Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### Database (SQLite)
```bash
python manage.py migrate
python manage.py shell
```

### Template Testing
Test component rendering directly:
```python
from storefront.utils.component_renderer import render_single_component
html = render_single_component({'type': 'hero', ...})
```

### Supabase Queries
```python
from storefront.client import get_supabase_client
supabase = get_supabase_client()
response = supabase.table('posts').select('*').eq('business_id', bid).execute()
posts = response.data
```

## Testing & Debugging Tips

### Check Subdomain Extraction
Request a URL like `http://alice.localhost:8000/` and inspect:
```python
print(request.subdomain)  # should be 'alice'
print(request.full_host)  # should be 'alice.localhost'
```

### Debug Component Rendering
Use the component normalizer:
```python
from storefront.utils.component_renderer import normalize_component_data
normalized = normalize_component_data(raw_component)
print(normalized.get('clean_type'))  # check mapped type
```

### Check Supabase Connection
Run in Django shell:
```python
from storefront.client import get_supabase_client
supabase = get_supabase_client()
print(supabase)  # should show client object
```

## Known Quirks & Gotchas

1. **Components as JSON strings** - Business components may be stored as JSON strings, not lists. Always parse: `json.loads(components_raw) if isinstance(components_raw, str) else components_raw`

2. **Image field order** - Products can have images in multiple places: `post_data['images']`, `post_data['thumbnailUrl']`, `post_data['imageUrl']`. Check in order and fallback gracefully.

3. **Type name inconsistencies** - A component might be `ProfileTestimonialComponent`, `testimonial`, or `testimonials`. The `type_mapping` dict handles this, but always test with real Supabase data.

4. **Subdomain localhost support** - Localhost subdomains only work if `ALLOW_LOCALHOST_SUBDOMAINS=True` in settings.

5. **CORS for forms** - Cross-subdomain forms require proper CORS setup and `CSRF_TRUSTED_ORIGINS` config.

## Key Supabase Tables
- `business_profiles` - Store business data, components, metadata
- `posts` - Store products/content
- `categories` - Product categories
- `auth.users` - User authentication

Query pattern: `supabase.table(table_name).select(columns).eq(field, value).execute()`

## Code Style & Patterns
- Use `logger = logging.getLogger(__name__)` for debugging
- Exception handling: log, then render fallback HTML or raise Http404
- Template context: always include `business` dict for navbar/footer
- View naming: `{action}_view` (e.g., `product_detail`, `login_view`)
- Import organization: Django → local modules → third-party

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
