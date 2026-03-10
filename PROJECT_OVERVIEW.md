# Nexus Web Project - Complete Overview

**Current Date**: March 10, 2026  
**Framework**: Django 6.0  
**Backend Database**: Supabase (PostgreSQL)  
**Frontend**: Django Templates + JavaScript  
**Deployment**: Render.com

---

## 1. Project Purpose & Architecture

### What is Nexus Web?

Nexus Web is a **multi-tenant SaaS storefront platform** built on Django 6.0 and Supabase. It allows multiple businesses to operate branded online shops through subdomains (e.g., `alice.nexassearch.com`, `bob.nexassearch.com`).

**Key Features:**
- Multi-tenant architecture using subdomains
- Dynamic shop customization via component system
- Product management and ordering
- User authentication (Google OAuth, email/password)
- Community features (lost & found, community posts, item swaps)
- News/blog functionality
- SEO-optimized with sitemaps and robots.txt
- Google Merchant integration

### Core Architecture Flow

```
HTTP Request (e.g., alice.nexassearch.com/product/123)
    ↓
[SubdomainMiddleware] → Extract subdomain from hostname
    ↓
[Django URL Router] (storefront/urls.py) → Route to correct view
    ↓
[View Handler] (storefront/views/*.py) → Process request
    ↓
[Supabase Client] → Fetch business data, products, user info
    ↓
[Component Normalization] → Map DB types to template names
    ↓
[Template Rendering] → Render Django HTML template
    ↓
[HTTP Response] → Send rendered HTML to browser
```

---

## 2. Core Components & Concepts

### 2.1 Subdomain-Based Multi-Tenancy

**How it works:**
- Each business gets its own subdomain (`alice.localhost`, `bob.localhost`, etc.)
- The `SubdomainMiddleware` (in `core/middleware.py`) extracts the subdomain from the hostname
- Views use `request.subdomain` to identify which business to serve
- Database queries filter by business domain/slug

**Example:**
```python
# In a view
subdomain = request.subdomain  # "alice"
supabase = get_supabase_client()
business = supabase.table('business_profiles').eq('domain', subdomain).select('*').execute()
```

**Middleware Details** (`core/middleware.py`):
- Parses hostname to extract subdomain
- Handles three cases:
  1. Primary domain (`nexassearch.com`) → `request.subdomain = None`
  2. Localhost subdomains (`alice.localhost`) → `request.subdomain = 'alice'` (if enabled)
  3. Generic multi-label hosts (`shop.test.local`) → Extracts first label as subdomain
- Sets `request.full_host` for reference

### 2.2 Component System

Components are the core of shop customization. Each business's Supabase profile contains an array of components that define page structure.

**Component Types** (from `storefront/views/shop.py`):
```
services, features, downloads, tabs, gallery, testimonials, team, faq, pricing,
hero, bio, contact, video, booking, portfolio, timeline, map, cta, heading, divider, awards
```

**Component Normalization (`normalize_component_data()`)**:
The database stores components with names like `ProfileServicesComponent`, but templates expect `services.html`. The normalizer:
1. Strips `Profile` and `Component` prefixes
2. Converts to lowercase
3. Maps to actual template filenames via `type_mapping` dict
4. Returns component with `clean_type` field for template lookup

Example:
```python
raw: {'type': 'ProfileServicesComponent', 'title': '...'}
normalized: {'type': 'ProfileServicesComponent', 'clean_type': 'services', 'title': '...'}
# Template expects: storefront/templates/storefront/components/services.html
```

### 2.3 Product Data Structure

Products are stored in Supabase `posts` table with JSON `data` field:
```python
{
  'id': 'uuid',
  'business_id': 'uuid',
  'data': {
    'productName': 'Cool T-Shirt',
    'productPrice': 29.99,
    'images': [{
      'url': 'https://...',
      'alt': 'Image description'
    }],
    'description': 'HTML content',
    'category': 'clothing'
  },
  'created_at': '2026-03-10T...'
}
```

**Safe Data Access Pattern**:
```python
post_data = post.get('data', {})  # Fallback to empty dict
product_name = post_data.get('productName', 'Untitled')
images = post_data.get('images', [])
```

---

## 3. Project Structure & Key Files

### Directory Layout

```
nexus_web/
├── core/                          # Django core settings & middleware
│   ├── settings.py               # Django configuration, ALLOWED_HOSTS, DEBUG
│   ├── middleware.py             # SubdomainMiddleware
│   ├── urls.py                   # Main URL router
│   ├── wsgi.py & asgi.py         # Production servers (Render)
│
├── storefront/                    # Main application
│   ├── models.py                 # Django ORM models (Category, Product, SupportTicket, etc.)
│   ├── urls.py                   # URL patterns for storefront routes
│   ├── client.py                 # Supabase client initialization
│   │
│   ├── views/                    # Request handlers
│   │   ├── shop.py              # Shop homepage, component normalization
│   │   ├── product.py           # Product detail, category filtering
│   │   ├── auth.py              # Login/signup, Google OAuth
│   │   ├── profile.py           # User profile views
│   │   ├── contact.py           # Contact form handling
│   │   ├── order.py             # Order confirmation
│   │   ├── wishlist.py          # Wishlist toggle/status
│   │   ├── robots.py            # robots.txt generation
│   │   ├── seo_views.py         # SEO-related views (user profiles, business profiles)
│   │   ├── sections.py          # Lost & found, community, swap sections
│   │   ├── pages.py             # Static pages (about, contact, newsletter, etc.)
│   │   ├── news.py              # News/blog articles
│   │   └── google_merchant.py   # Google Merchant CSV/XML export
│   │
│   ├── utils/                    # Utility functions
│   │   └── component_renderer.py # render_component_list(), render_single_component()
│   │
│   ├── templates/storefront/    # HTML templates (Jinja2)
│   │   ├── base.html            # Root template with LocalBusiness schema
│   │   ├── shop_home.html       # Homepage template
│   │   ├── login.html           # Login page
│   │   ├── signup.html          # Signup page
│   │   ├── components/          # Component templates (services, features, etc.)
│   │   ├── partials/            # Reusable template parts (navbar, footer, etc.)
│   │   └── pages/               # Static page templates (about, contact, etc.)
│   │
│   └── migrations/              # Database migrations
│
├── nexus-app/                    # React Native mobile app (Expo)
│   ├── app/                      # Expo Router navigation
│   ├── components/               # React components
│   └── services/                 # API services (supabase.ts)
│
├── staticfiles/                  # Deployed static assets (CSS, JS)
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
└── .env                         # Environment variables (not in git)
```

---

## 4. Request Handling Flow (Example)

**Request**: `GET https://alice.localhost:8000/product/550e8400-e29b-41d4-a716-446655440000`

**Step-by-step:**

1. **Middleware Processing**:
   - `SubdomainMiddleware` extracts `alice` from `alice.localhost`
   - Sets `request.subdomain = 'alice'`, `request.full_host = 'alice.localhost'`

2. **URL Routing** (`storefront/urls.py`):
   - Matches pattern: `path('product/<uuid:product_id>/', product_detail, name='product_detail')`
   - Calls `product_detail(request, product_id=uuid)`

3. **View Execution** (`storefront/views/product.py`):
   ```python
   def product_detail(request, product_id):
       subdomain = request.subdomain  # "alice"
       supabase = get_supabase_client()
       
       # Fetch business
       business = supabase.table('business_profiles')\
           .eq('domain', subdomain)\
           .select('*')\
           .execute()
       
       # Fetch product
       product = supabase.table('posts')\
           .eq('id', product_id)\
           .select('*')\
           .execute()
       
       context = {
           'business': business.data[0],
           'product': product.data[0],
       }
       return render(request, 'storefront/product_detail.html', context)
   ```

4. **Template Rendering**:
   - Renders `storefront/templates/storefront/product_detail.html`
   - Has access to business and product data
   - Includes SEO meta tags, LocalBusiness schema, product images

5. **Response**: HTML sent to browser

---

## 5. Views & URL Mapping

### Key Views (`storefront/views/`)

| View Function | File | URL Pattern | Purpose |
|---|---|---|---|
| `shop_home()` | shop.py | `/` | Homepage, displays business components & featured products |
| `product_detail()` | product.py | `/product/<uuid>/` | Product detail page with images, description, order form |
| `category_view()` | product.py | `/category/<name>/` | Products filtered by category |
| `login_view()` | auth.py | `/login/` | Email/password login |
| `google_login_view()` | auth.py | `/login/google/` | Google OAuth flow |
| `signup_view()` | auth.py | `/signup/` | User registration |
| `auth_callback_view()` | auth.py | `/auth/callback/` | Supabase OAuth callback |
| `logout_view()` | auth.py | `/logout/` | User logout |
| `profile_view()` | profile.py | `/profile/` | User profile dashboard |
| `toggle_wishlist()` | wishlist.py | `/wishlist/toggle/<uuid>/` | Add/remove from wishlist |
| `lost_and_found_view()` | sections.py | `/lost-and-found/` | Lost & found items listing |
| `community_view()` | sections.py | `/community/` | Community posts |
| `swap_view()` | sections.py | `/swap/` | Item swap listings |
| `news_list()` | news.py | `/news/` | News/blog articles |
| `robots_txt()` | robots.py | `/robots.txt` | SEO robots directives |
| `contact_view()` | pages.py | `/contact/` | Contact form page |

### URL Patterns (`storefront/urls.py`)

All URLs are multi-tenant aware—they work with any subdomain. Example: `/product/123/` works for both `alice.localhost` and `bob.localhost`, serving Alice's or Bob's product respectively.

---

## 6. Django App Lifecycle

### Settings (`core/settings.py`)

**Key Settings:**
- `DEBUG`: Read from `.env` (default: `False`)
- `SECRET_KEY`: Must be set in `.env` for production
- `ALLOWED_HOSTS`: Includes `.nexassearch.com`, `.localhost`, `.onrender.com`, `localhost`, `127.0.0.1`
- `ALLOW_LOCALHOST_SUBDOMAINS`: Toggle localhost subdomain support (default: `True`)
- `INSTALLED_APPS`: `storefront` (main app)
- `MIDDLEWARE`: SubdomainMiddleware runs before Django's middleware stack
- `DATABASES`: SQLite for dev, PostgreSQL for production
- `STATIC_URL`: WhiteNoise serves static files

**Middleware Stack** (order matters):
1. `CorsMiddleware` (for CORS headers)
2. `SubdomainMiddleware` (extract subdomain)
3. `ExceptionMiddleware` (error handling)
4. Standard Django middleware
5. `WhiteNoiseMiddleware` (serve static files)

### Models (`storefront/models.py`)

Django ORM models for local SQLite database (optional, mostly using Supabase):

```python
class Category(models.Model):
    name = CharField
    icon = ImageField

class Product(models.Model):
    name, price, rating, review_count, image, category, is_favorite

class ContactSubmission(models.Model):
    name, email, message, created_at

class SupportTicket(models.Model):
    user_id, subject, description, status, priority, created_at, updated_at

class SupportMessage(models.Model):
    ticket (FK), sender_id, message
```

---

## 7. Database Architecture

### Supabase Tables

The main data lives in Supabase (PostgreSQL). Local SQLite models are mostly for support tickets and contact forms.

**Key Supabase Tables:**
- `business_profiles` - Business metadata, components, logos, status (active/inactive)
- `posts` - Products and content (stores JSON `data` field)
- `categories` - Product categories
- `users` - User authentication & profiles (via Supabase Auth)
- `orders` - Order records
- `wishlist_items` - User wishlist entries
- `lost_found_items` - Lost & found posts
- `community_posts` - Community discussion posts
- `swap_items` - Item swap listings
- `news_articles` - Blog/news articles

**Data Fetching Pattern**:
```python
from storefront.client import get_supabase_client

supabase = get_supabase_client()

# Fetch business by domain
business = supabase\
    .table('business_profiles')\
    .eq('domain', request.subdomain)\
    .select('*')\
    .execute()

# Fetch products by category
products = supabase\
    .table('posts')\
    .eq('business_id', business_id)\
    .eq('data->category', 'clothing')\
    .select('*')\
    .execute()
```

---

## 8. Component Rendering System

### How Components Render

1. **Fetch from Supabase**:
   ```python
   business = supabase.table('business_profiles')\
       .eq('domain', subdomain).select('*').execute()
   components = business.data[0].get('components', [])
   ```

2. **Normalize Types** (`normalize_component_data()`):
   ```python
   for component in components:
       normalized = normalize_component_data(component)
       # normalized has 'clean_type': 'services', 'features', etc.
   ```

3. **Render to HTML** (`render_component_list()`):
   ```python
   from storefront.utils.component_renderer import render_component_list
   components_html = render_component_list(normalized_components)
   ```

4. **Include in Template**:
   ```django
   {{ components_html|safe }}
   ```

### Component Templates Location

- `storefront/templates/storefront/components/services.html`
- `storefront/templates/storefront/components/features.html`
- `storefront/templates/storefront/components/gallery.html`
- ... etc for all component types

**Template Variables**: Each template receives the full component dict via context:
```django
<!-- In services.html -->
<h2>{{ component.title }}</h2>
{% for service in component.items %}
  <div>{{ service.name }} - {{ service.description }}</div>
{% endfor %}
```

---

## 9. Authentication System

### Authentication Methods

1. **Email/Password**:
   - Form submission on `/login/` or `/signup/`
   - Calls Supabase Auth API
   - Creates JWT token stored in browser

2. **Google OAuth**:
   - Click "Login with Google" → `/login/google/`
   - Redirects to Google/Supabase OAuth flow
   - Callback at `/auth/callback/`
   - User confirmed at `/auth/confirm/`

### Auth Views (`storefront/views/auth.py`)

- `login_view()` - Form-based email login
- `signup_view()` - New user registration
- `google_login_view()` - Google OAuth redirect
- `auth_callback_view()` - Supabase auth callback
- `confirm_auth_view()` - Confirm user after OAuth

### Session Management

- Supabase JWT tokens stored in browser cookies
- Subsequent API calls include token in header
- Logout clears token

---

## 10. SEO & Sitemap Strategy

### Robots.txt (`storefront/views/robots.py`)

Routes to `/robots.txt` and tells search engines:
```
User-agent: *
Allow: /
Sitemap: https://nexassearch.com/static/sitemaps/sitemap_index.xml
```

### Sitemaps

1. **Sitemap Index** (`sitemap_index.py`):
   - Lists all published businesses
   - Points to individual `sitemap.xml` for each

2. **Per-Business Sitemap** (`sitemap.py`):
   - Lists all products for that business
   - Includes image URLs for product images
   - Only includes "active" published businesses

3. **Static Sitemaps Cache**:
   - Pre-generated XML files in `storefront/static/sitemaps/`
   - Updated via `run_sitemap_generation.py` script
   - Reduces dynamic database calls

### Schema Markup (SEO)

**In `base.html`**: LocalBusiness schema in `<head>`:
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Alice's Shop",
  "url": "https://alice.nexassearch.com",
  "image": "logo_url",
  "description": "Shop bio"
}
```

**In product template**: Product schema:
```json
{
  "@type": "Product",
  "name": "Product Name",
  "price": "29.99",
  "image": "image_urls",
  "description": "Description"
}
```

---

## 11. Key Scripts & Utilities

### Scripts (in project root)

| Script | Purpose |
|---|---|
| `run_sitemap_generation.py` | Pre-generate all static sitemaps for all businesses |
| `check_business_status.py` | Check how many businesses are active/inactive/pending |
| `validate_production_sitemaps.py` | Validate sitemap XML structure |
| `check_db_businesses.py` | Query database for businesses |
| `check_data.py` | General data inspection |
| `verify_auth_system.py` | Auth flow diagnostics |
| `verify_theme_css.py` | Theme CSS validation |

### Utilities (`storefront/utils/`)

**`component_renderer.py`**:
- `render_component_list(components)` - Renders multiple components to HTML
- `render_single_component(component)` - Renders one component
- `render_legacy_component()` - Fallback for old content types
- Type mapping system for template resolution

---

## 12. Static Assets & Frontend

### CSS & JavaScript

- `storefront/theme.css` - Custom theme styles
- `staticfiles/css/theme-variables.css` - CSS variables for branding
- `js/seo-helpers.js` - SEO helper functions
- `js/supabase-config.js` - Supabase client config
- Compiled by Django's `collectstatic` command

### Frontend Libraries

- **Django Templates** (Jinja2 syntax) for server-side rendering
- **JavaScript** for interactivity (wishlist, cart, etc.)
- **Expo (React Native)** for mobile app (`nexus-app/`)

---

## 13. Configuration & Environment

### `.env` File (Required)

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True  # or False for production
ALLOWED_HOSTS=.localhost,localhost,127.0.0.1
ALLOW_LOCALHOST_SUBDOMAINS=True

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email (if using email forms)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

### Dependencies (`requirements.txt`)

```
Django>=4.2             # Web framework
python-dotenv>=1.0.0    # .env file support
supabase>=1.0.0         # Supabase Python client
requests>=2.28          # HTTP library
gunicorn>=20.1.0        # Production server
whitenoise>=6.0         # Static file serving
psycopg2-binary>=2.9    # PostgreSQL adapter
django-cors-headers    # CORS support
```

---

## 14. Deployment Architecture

### Render.com Deployment

- **Web Service**: Django app runs on Gunicorn
- **Build Command**: `pip install -r requirements.txt; python manage.py migrate; python manage.py collectstatic --noinput`
- **Start Command**: `gunicorn core.wsgi:application`
- **Environment**: Production settings with PostgreSQL

### Static Files

- **WhiteNoise Middleware**: Serves static files efficiently
- **Sitemaps Cache**: Pre-generated in `storefront/static/sitemaps/`
- **Collected via**: `python manage.py collectstatic`

---

## 15. Common Workflows & Tasks

### Running Locally

```bash
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env with Supabase credentials
echo "SUPABASE_URL=..." > .env
echo "SUPABASE_KEY=..." >> .env

# Run migrations (if using local SQLite)
python manage.py migrate

# Start dev server
python manage.py runserver 0.0.0.0:8000

# Visit: http://alice.localhost:8000
```

### Adding a New Component Type

1. **Add Type Mapping** in `storefront/views/shop.py`:
   ```python
   type_mapping = {
       'mycomponent': 'mycomponent',  # Add entry
       ...
   }
   ```

2. **Create Template** at:
   ```
   storefront/templates/storefront/components/mycomponent.html
   ```

3. **Render Component** (automatic via `render_component_list()`)

### Updating Sitemaps

```bash
python run_sitemap_generation.py
# Creates/updates storefront/static/sitemaps/sitemap_index.xml and individual sitemaps
```

### Checking Business Status

```bash
python check_business_status.py
# Shows count of active, inactive, pending businesses
```

---

## 16. Known Quirks & Best Practices

### ✅ Safe Data Access

Always use `.get()` with defaults:
```python
post_data = post.get('data', {})
images = post_data.get('images', [])
product_name = post_data.get('productName', 'Untitled')
```

### ✅ Component Type Mapping

The `type_mapping` dict in `normalize_component_data()` is the single source of truth. If a component doesn't render:
1. Check raw type from Supabase
2. Add entry to `type_mapping` dict
3. Ensure template exists at correct path

### ✅ Subdomain Extraction

Always check if subdomain exists before use:
```python
if request.subdomain is None:
    return redirect('/')  # Redirect to JS frontend
business = get_business_by_domain(request.subdomain)
```

### ✅ JSON Components

Business components may be stored as JSON strings, always parse:
```python
components = business.get('components', [])
if isinstance(components, str):
    components = json.loads(components)
```

### ⚠️ Common Pitfalls

- **Missing template**: Component type mapped but no HTML template → blank output
- **Wrong data keys**: Different products use different JSON field names (e.g., `imageUrl` vs `thumbnailUrl` vs `images`)
- **Status filtering**: Only "active" businesses appear in sitemaps, inactive ones won't show up in search
- **Stale cache**: Old sitemaps in `staticfiles/` not updated when businesses change

---

## 17. System Integrations

### Google Merchant Integration

- `storefront/views/google_merchant.py` exports product feeds
- `/merchant/products.csv` - CSV product feed
- `/merchant/products.xml` - XML product feed for Google Shopping

### Supabase Realtime (Optional)

- Can subscribe to database changes via Supabase client
- Useful for wishlist updates, order notifications
- Not currently used but infrastructure supports it

### Email Integration (Optional)

- Contact form can send emails via SMTP
- Configured in settings via `EMAIL_*` variables
- Templates in `storefront/templates/storefront/contact/`

---

## 18. Testing & Debugging

### Debug Mode

In `.env`:
```env
DEBUG=True
```

Enables:
- Detailed error pages
- Django Debug Toolbar
- Static file serving

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Variable value: %s", var)
logger.info("Process step complete")
logger.warning("Potential issue: %s", issue)
logger.error("Error occurred: %s", error)
```

### Django Shell

```bash
python manage.py shell

>>> from storefront.client import get_supabase_client
>>> supabase = get_supabase_client()
>>> biz = supabase.table('business_profiles').eq('domain', 'alice').select('*').execute()
>>> print(biz.data[0] if biz.data else 'Not found')
```

### Component Testing

```python
from storefront.views.shop import normalize_component_data
from storefront.utils.component_renderer import render_single_component

comp = {'type': 'ProfileServicesComponent', 'title': 'My Services'}
normalized = normalize_component_data(comp)
html = render_single_component(normalized)
print(html)
```

---

## 19. File Structure Summary

```
Nexus Web/
│
├─ Core (Django Configuration)
│  ├─ core/settings.py           ← Main config (ALLOWED_HOSTS, MIDDLEWARE, DEBUG)
│  ├─ core/middleware.py          ← Subdomain extraction logic
│  ├─ core/urls.py               ← Root URL dispatcher
│
├─ Storefront (Main App)
│  ├─ storefront/urls.py         ← All route patterns
│  ├─ storefront/models.py       ← Django ORM models
│  ├─ storefront/client.py       ← Supabase connection
│  │
│  ├─ Views (Request Handlers)
│  │  ├─ views/shop.py           ← Homepage, component normalization
│  │  ├─ views/product.py        ← Product pages
│  │  ├─ views/auth.py           ← User authentication
│  │  ├─ views/profile.py        ← User profiles
│  │  ├─ views/order.py          ← Order confirmation
│  │  ├─ views/wishlist.py       ← Wishlist management
│  │  ├─ views/robots.py         ← robots.txt generation
│  │  ├─ views/seo_views.py      ← SEO-optimized views
│  │  └─ views/[...].py          ← Other feature views
│  │
│  ├─ Utils (Helpers)
│  │  └─ utils/component_renderer.py ← Component HTML generation
│  │
│  ├─ Templates (HTML)
│  │  ├─ templates/base.html     ← Root template
│  │  ├─ templates/components/   ← Component templates
│  │  └─ templates/pages/        ← Page templates
│  │
│  └─ Migrations (Database Schema)
│     └─ migrations/
│
├─ Mobile App (Expo/React Native)
│  └─ nexus-app/                 ← React Native mobile app
│
├─ Static Assets
│  ├─ staticfiles/               ← Collected by collectstatic
│  └─ storefront/static/         ← Static files source
│
├─ Scripts (Utilities)
│  ├─ run_sitemap_generation.py
│  ├─ check_business_status.py
│  └─ [other admin scripts]
│
└─ Configuration
   ├─ manage.py                  ← Django management command
   ├─ requirements.txt           ← Python dependencies
   ├─ .env                       ← Environment variables (not in git)
   └─ Procfile                   ← Render deployment config
```

---

## 20. Key Takeaways

1. **Multi-Tenant via Subdomains**: Each business serves from its own subdomain using the same Django codebase
2. **Component-Driven UI**: Businesses customize their shops by adding/configuring components (services, gallery, etc.)
3. **Supabase Backend**: All data lives in Supabase PostgreSQL; Django models are minimal
4. **Server-Side Rendering**: Django templates render HTML on server, sent to browser
5. **SEO-Optimized**: Sitemaps, robots.txt, schema markup for search engines
6. **Multi-Feature**: Products, orders, user profiles, community, lost & found, item swaps, news
7. **Authentication**: Email/password and Google OAuth via Supabase
8. **Deployment**: Render.com with Gunicorn, WhiteNoise for static files

---

## Next Steps for Development

1. **Add new component type** → Add type_mapping entry + create template
2. **Add new feature** → Create view in `storefront/views/`, add URL pattern, create templates
3. **Debug issues** → Use Django shell, logging, check Supabase data directly
4. **Deploy changes** → Push to git, Render auto-deploys from main branch
5. **Update sitemaps** → Run `python run_sitemap_generation.py` after adding products

---

**Last Updated**: March 10, 2026
