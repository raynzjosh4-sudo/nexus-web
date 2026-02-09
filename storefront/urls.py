from django.urls import path
from . import views
from django.urls import path
# Import from the NEW files
from .views.shop import shop_home
from .views.shop import shop_home
from .views.product import product_detail, category_view, create_order
from .views.auth import login_view, logout_view, google_login_view, auth_callback_view, confirm_auth_view
from .views.profile import profile_view
from .views.contact import contact
from .views.wishlist import toggle_wishlist, check_wishlist_status
from .views.sitemap_static import sitemap_products, sitemap_index, serve_sitemap_file  # PRODUCTION: Static sitemaps
from .views.robots import robots_txt
from .views.order import order_confirmation
from .views.sections import lost_and_found_view, community_view, swap_view, help_view
from .views.seo_views import (
    community_detail_view,
    lost_found_detail_view,
    swap_detail_view,
    user_profile_view,
    business_profile_view,
    category_list_view,
    faq_view,
)

urlpatterns = [
    path('', shop_home, name='shop_home'),
    path('contact/', contact, name='contact'),
    path('product/<uuid:product_id>/', product_detail, name='product_detail'),
    path('product/<uuid:product_id>/order/', create_order, name='create_order'),
    path('order/<uuid:order_id>/confirmation/', order_confirmation, name='order_confirmation'),
    path('category/<str:category_name>/', category_view, name='category_view'),
    path('login/', login_view, name='login'),
    path('signup/', views.auth.signup_view, name='signup'),
    path('login/google/', google_login_view, name='google_login'),
    path('auth/callback/', auth_callback_view, name='auth_callback'),
    path('auth/confirm/', confirm_auth_view, name='confirm_auth'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('wishlist/toggle/<uuid:product_id>/', toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/status/<uuid:product_id>/', check_wishlist_status, name='check_wishlist_status'),
    path('lost-and-found/', lost_and_found_view, name='lost_and_found'),
    path('lost-and-found/<uuid:item_id>/', lost_found_detail_view, name='lost_found_detail'),
    path('community/', community_view, name='community'),
    path('community/<uuid:post_id>/', community_detail_view, name='community_detail'),
    path('swap/', swap_view, name='swap'),
    path('swap/<uuid:swap_id>/', swap_detail_view, name='swap_detail'),
    path('help/', help_view, name='help'),
    path('u/<str:username>/', user_profile_view, name='user_profile'),
    path('business/<str:business_slug>/', business_profile_view, name='business_profile'),
    path('faq/', faq_view, name='faq'),
    path('category/<str:category_name>/', category_list_view, name='category_list_seo'),
    path('sitemap.xml', sitemap_products, name='sitemap_products'),
    path('sitemap_index.xml', sitemap_index, name='sitemap_index'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('static/sitemaps/<str:filename>', serve_sitemap_file, name='serve_sitemap_file'),
]