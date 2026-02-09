"""
SEO-Optimized Views for Nexus Marketplace
Handles Community, Lost & Found, Swap, User Profiles, Business Profiles
with proper schema markup for Google indexing
"""

import json
import logging
from datetime import datetime
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.http import condition
from ..client import get_supabase_client

logger = logging.getLogger(__name__)


def get_supabase():
    """Get Supabase client"""
    return get_supabase_client()


def build_json_ld_schema(schema_type, data):
    """Build JSON-LD schema for SEO"""
    base_schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
    }
    
    if schema_type == "DiscussionForumPosting":
        # Community Question/Post
        return {
            **base_schema,
            "headline": data.get('title', 'Community Post'),
            "description": data.get('body', data.get('description', ''))[:500],
            "text": data.get('body', data.get('description', '')),
            "image": data.get('image_url', ''),
            "datePublished": data.get('created_at', ''),
            "dateModified": data.get('updated_at', data.get('created_at', '')),
            "author": {
                "@type": "Person",
                "name": data.get('author', data.get('user_name', 'Anonymous'))
            },
            "publisher": {
                "@type": "Organization",
                "name": "Nexus - Uganda Marketplace",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://nexassearch.com/logo.png"
                }
            },
            "keywords": f"{data.get('category', 'general')}, community, Uganda",
            "inLanguage": "en-UG",
            "isAccessibleForFree": True
        }
    
    elif schema_type == "Article":
        # Lost & Found Documents
        return {
            **base_schema,
            "headline": data.get('title', 'Lost & Found'),
            "description": data.get('description', '')[:500],
            "articleBody": data.get('description', ''),
            "image": data.get('image', ''),
            "datePublished": data.get('created_at', ''),
            "dateModified": data.get('updated_at', data.get('created_at', '')),
            "author": {
                "@type": "Person",
                "name": data.get('contact_value', data.get('user_name', 'Anonymous'))
            },
            "publisher": {
                "@type": "Organization",
                "name": "Nexus Lost & Found",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://nexassearch.com/logo.png"
                }
            },
            "inLanguage": "en-UG",
            "keywords": f"lost, found, {data.get('location_name', '')}, Uganda"
        }
    
    elif schema_type == "Product":
        # Swap items and products
        price = data.get('price', 0)
        return {
            **base_schema,
            "name": data.get('title', data.get('productName', 'Product')),
            "description": data.get('description', data.get('snippet', ''))[:500],
            "image": data.get('image', data.get('image_url', '')),
            "brand": {
                "@type": "Brand",
                "name": data.get('seller_name', 'Individual Seller')
            },
            "offers": {
                "@type": "Offer",
                "url": f"https://nexassearch.com/product/{data.get('id', '')}",
                "priceCurrency": "UGX",
                "price": str(price),
                "availability": "https://schema.org/InStock",
                "seller": {
                    "@type": "Person",
                    "name": data.get('seller_name', 'Seller')
                }
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": data.get('rating', '4.5'),
                "reviewCount": data.get('review_count', '0')
            },
            "inLanguage": "en-UG",
            "keywords": f"{data.get('category', '')}, swap, trade, Uganda"
        }
    
    elif schema_type == "ProfilePage":
        # User Profile
        return {
            **base_schema,
            "name": data.get('full_name', data.get('username', 'User')),
            "description": data.get('bio', ''),
            "image": data.get('avatar_url', ''),
            "sameAs": [
                f"https://nexassearch.com/u/{data.get('username', '')}"
            ],
            "dateModified": data.get('updated_at', ''),
            "author": {
                "@type": "Person",
                "name": data.get('full_name', data.get('username', 'User'))
            }
        }
    
    elif schema_type == "LocalBusiness":
        # Business Profile
        return {
            **base_schema,
            "name": data.get('business_name', ''),
            "description": data.get('description', ''),
            "image": data.get('logo_url', ''),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": data.get('address', ''),
                "addressLocality": data.get('city', 'Kampala'),
                "addressRegion": data.get('region', 'Uganda'),
                "postalCode": data.get('postal_code', ''),
                "addressCountry": "UG"
            },
            "telephone": data.get('phone', ''),
            "url": f"https://nexassearch.com/business/{data.get('slug', data.get('domain', ''))}",
            "email": data.get('email', ''),
            "priceRange": data.get('price_range', '$$'),
            "sameAs": data.get('social_links', []),
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": data.get('latitude', ''),
                "longitude": data.get('longitude', '')
            },
            "openingHoursSpecification": data.get('opening_hours', []),
            "inLanguage": "en-UG"
        }
    
    return base_schema


def community_detail_view(request, post_id):
    """
    Community Question/Post Detail Page
    SEO: DiscussionForumPosting Schema
    URL: /community/detail/<uuid>/
    """
    try:
        supabase = get_supabase()
        
        # Fetch the post
        response = supabase.table('community_posts').select('*').eq('id', post_id).single().execute()
        
        if not response.data:
            raise Http404("Post not found")
        
        post = response.data
        
        # Build SEO context
        schema = build_json_ld_schema('DiscussionForumPosting', post)
        
        context = {
            'post': post,
            'title': post.get('title', 'Community Post'),
            'meta_description': (post.get('body', post.get('description', ''))[:155]),
            'og_image': post.get('image_url', ''),
            'schema_json': json.dumps(schema),
            'canonicalUrl': f"https://nexassearch.com/community/{post_id}/",
        }
        
        return render(request, 'storefront/pages/community_detail.html', context)
    
    except Exception as e:
        logger.error(f"Error loading community post {post_id}: {str(e)}")
        raise Http404("Post not found")


def lost_found_detail_view(request, item_id):
    """
    Lost & Found Item Detail Page
    SEO: Article Schema
    URL: /lost-and-found/detail/<uuid>/
    """
    try:
        supabase = get_supabase()
        
        # Fetch the item
        response = supabase.table('lost_found_items').select('*').eq('id', item_id).single().execute()
        
        if not response.data:
            raise Http404("Item not found")
        
        item = response.data
        
        # Build SEO context
        schema = build_json_ld_schema('Article', item)
        
        context = {
            'item': item,
            'title': f"{item.get('title', 'Lost Item')} - Found in {item.get('location_name', 'Uganda')}",
            'meta_description': (item.get('description', '')[:155]),
            'og_image': item.get('image', ''),
            'schema_json': json.dumps(schema),
            'canonicalUrl': f"https://nexassearch.com/lost-and-found/{item_id}/",
        }
        
        return render(request, 'storefront/pages/lost_found_detail.html', context)
    
    except Exception as e:
        logger.error(f"Error loading lost item {item_id}: {str(e)}")
        raise Http404("Item not found")


def swap_detail_view(request, swap_id):
    """
    Swap/Exchange Item Detail Page
    SEO: Product Schema
    URL: /swap/<uuid>/
    """
    try:
        supabase = get_supabase()
        
        # Fetch the swap item
        response = supabase.table('swap_items').select('*').eq('id', swap_id).single().execute()
        
        if not response.data:
            raise Http404("Swap item not found")
        
        swap = response.data
        
        # Handle image_urls array - get first image if available
        image_urls = swap.get('image_urls', [])
        featured_image = image_urls[0] if isinstance(image_urls, list) and len(image_urls) > 0 else ''
        
        # Build SEO context
        schema = build_json_ld_schema('Product', {**swap, 'image': featured_image})
        
        context = {
            'swap': swap,
            'featured_image': featured_image,
            'title': f"Swap: {swap.get('title', 'Item')} for {swap.get('want_title', '')}",
            'meta_description': f"Free trade/swap: {swap.get('description', '')[:155]}",
            'og_image': featured_image,
            'schema_json': json.dumps(schema),
            'canonicalUrl': f"https://nexassearch.com/swap/{swap_id}/",
        }
        
        return render(request, 'storefront/pages/swap_detail.html', context)
    
    except Exception as e:
        logger.error(f"Error loading swap item {swap_id}: {str(e)}")
        raise Http404("Swap item not found")


def user_profile_view(request, username):
    """
    User Profile Page
    SEO: ProfilePage Schema
    URL: /u/<username>/
    """
    try:
        supabase = get_supabase()
        
        # Fetch the user by slug (username equivalent in nexususers table)
        response = supabase.table('nexususers').select('*').eq('slug', username).single().execute()
        
        if not response.data:
            raise Http404("User not found")
        
        user = response.data
        user_id = user.get('id')
        
        # Fetch community posts from this user
        community_response = supabase.table('community_posts').select('*').eq('author_id', user_id).limit(8).execute()
        community_posts = community_response.data or []
        
        # Build SEO context
        schema = build_json_ld_schema('ProfilePage', user)
        
        context = {
            'user': user,
            'community_posts': community_posts,
            'title': f"{user.get('name', username)} - Nexus Marketplace Uganda",
            'meta_description': user.get('bio', f"Profile of {username} on Nexus Marketplace")[:155],
            'og_image': user.get('avatar_url', ''),
            'schema_json': json.dumps(schema),
            'canonicalUrl': f"https://nexassearch.com/u/{username}/",
        }
        
        return render(request, 'storefront/pages/user_profile.html', context)
    
    except Exception as e:
        logger.error(f"Error loading profile {username}: {str(e)}")
        raise Http404("User not found")


def business_profile_view(request, business_slug):
    """
    Business Profile Page
    SEO: LocalBusiness Schema
    URL: /business/<slug>/ or <business>.nexassearch.com
    """
    try:
        supabase = get_supabase()
        
        # Fetch the business by slug
        response = supabase.table('business_profiles').select('*').eq('slug', business_slug).single().execute()
        
        if not response.data:
            raise Http404("Business not found")
        
        business = response.data
        business_id = business.get('id')
        
        # Fetch business products (posts associated with this business)
        products_response = supabase.table('posts').select('*').eq('business_id', business_id).limit(12).execute()
        products = products_response.data or []
        
        # Build SEO context
        schema = build_json_ld_schema('LocalBusiness', business)
        
        context = {
            'business': business,
            'products': products,
            'title': f"{business.get('business_name', '')} - Uganda Marketplace",
            'meta_description': business.get('business_description', business.get('description', f"Shop at {business.get('business_name', '')}"))[:155],
            'og_image': business.get('logo_url', ''),
            'schema_json': json.dumps(schema),
            'canonicalUrl': f"https://nexassearch.com/business/{business_slug}/",
        }
        
        return render(request, 'storefront/pages/business_profile.html', context)
    
    except Exception as e:
        logger.error(f"Error loading business {business_slug}: {str(e)}")
        raise Http404("Business not found")


def category_list_view(request, category_name):
    """
    Category/Search Results Page
    SEO: BreadcrumbList + ItemList Schema
    URL: /category/<name>/
    """
    try:
        supabase = get_supabase()
        
        # Fetch items in category
        response = supabase.table('posts').select('*').eq('category', category_name).execute()
        items = response.data or []
        
        # Build BreadcrumbList schema
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://nexassearch.com"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": category_name,
                    "item": f"https://nexassearch.com/category/{category_name}/"
                }
            ]
        }
        
        # Build ItemList schema
        item_list_schema = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": category_name,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": idx + 1,
                    "item": {
                        "@type": "Product",
                        "name": item.get('title', item.get('productName', '')),
                        "image": item.get('image', ''),
                        "url": f"https://nexassearch.com/product/{item.get('id', '')}/",
                    }
                }
                for idx, item in enumerate(items[:20])
            ]
        }
        
        context = {
            'items': items,
            'category': category_name,
            'title': f"{category_name} - Buy, Sell, Swap on Nexus Uganda",
            'meta_description': f"Browse {category_name} items on Nexus Marketplace Uganda",
            'schema_json': json.dumps(breadcrumb_schema),
            'item_list_schema': json.dumps(item_list_schema),
            'canonicalUrl': f"https://nexassearch.com/category/{category_name}/",
        }
        
        return render(request, 'storefront/pages/category_list.html', context)
    
    except Exception as e:
        logger.error(f"Error loading category {category_name}: {str(e)}")
        raise Http404("Category not found")


def faq_view(request):
    """
    FAQ/Help Page
    SEO: FAQPage Schema
    URL: /faq/ or /safety-tips/
    """
    faqs = [
        {
            "question": "How do I list an item for sale?",
            "answer": "Sign up, click 'Sell', fill in the details, add photos, and publish. Your item appears on Nexus marketplace within minutes."
        },
        {
            "question": "Is it safe to meet strangers on Nexus?",
            "answer": "Yes! Always meet in public places, bring a friend, and never share personal information before meeting."
        },
        {
            "question": "What payment methods do you accept?",
            "answer": "We support Mobile Money (MTN, Airtel), Bank Transfers, and Cash on Pickup. All safe and secure."
        },
        {
            "question": "How do I swap items?",
            "answer": "Select the 'Swap' option when creating your listing, specify what you want in exchange, and wait for offers."
        },
        {
            "question": "Can I report a lost or found item?",
            "answer": "Yes! Use our Lost & Found section. Post photos and details to help reunite items with their owners."
        },
        {
            "question": "What areas does Nexus serve?",
            "answer": "We operate across Uganda with main activity in Kampala, but expanding to all regions."
        },
    ]
    
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"]
                }
            }
            for faq in faqs
        ]
    }
    
    context = {
        'faqs': faqs,
        'title': "Safety Tips & FAQ - Nexus Marketplace Uganda",
        'meta_description': "Learn how to safely buy, sell, and swap on Nexus. Get answers to common questions.",
        'schema_json': json.dumps(schema),
        'canonicalUrl': "https://nexassearch.com/faq/",
    }
    
    return render(request, 'storefront/pages/faq.html', context)
