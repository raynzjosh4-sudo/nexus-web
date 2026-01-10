from django.urls import path
from . import views
from django.urls import path
# Import from the NEW files
from .views.shop import shop_home
from .views.shop import shop_home
from .views.product import product_detail, category_view, create_order
from .views.auth import login_view, logout_view, google_login_view, auth_callback_view, confirm_auth_view
from .views.profile import profile_view
from .views.wishlist import toggle_wishlist, check_wishlist_status
urlpatterns = [
    path('', shop_home, name='shop_home'),
    path('product/<uuid:product_id>/', product_detail, name='product_detail'),
    path('product/<uuid:product_id>/order/', create_order, name='create_order'),
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
]