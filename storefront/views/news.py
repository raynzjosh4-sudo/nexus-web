import logging
from django.shortcuts import render
from django.http import Http404
from ..client import get_supabase_client

logger = logging.getLogger(__name__)

def news_list(request):
    """
    Display a list of news articles with pagination and filtering.
    """
    supabase = get_supabase_client()

    # Get query parameters for filtering
    category = request.GET.get('category', '')
    featured_only = request.GET.get('featured', '').lower() == 'true'

    # Build query
    query = supabase.table('news_articles').select('*, news_authors(name, avatar_url, title, organization, is_verified)')

    # Apply filters
    if category:
        query = query.eq('category', category)

    if featured_only:
        query = query.eq('is_featured', True)

    # Order by published date (newest first)
    query = query.order('published_at', desc=True)

    # Execute query
    try:
        response = query.execute()
        articles = response.data or []
    except Exception as e:
        logger.error(f"Error fetching news articles: {e}")
        articles = []

    # Get unique categories for filter dropdown
    categories = []
    if articles:
        try:
            category_response = supabase.table('news_articles').select('category').execute()
            categories = list(set([article['category'] for article in category_response.data if article.get('category')]))
            categories.sort()
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            categories = []

    # Separate featured and regular articles
    featured_articles = [article for article in articles if article.get('is_featured', False)]
    regular_articles = [article for article in articles if not article.get('is_featured', False)]

    # Get main featured article (first featured article)
    main_featured = featured_articles[0] if featured_articles else None
    # Remove main featured from the featured list for the sidebar
    sidebar_featured = featured_articles[1:] if len(featured_articles) > 1 else []

    context = {
        'main_featured': main_featured,
        'sidebar_featured': sidebar_featured,
        'regular_articles': regular_articles,
        'all_articles': articles,
        'categories': categories,
        'selected_category': category,
        'featured_only': featured_only,
        'total_articles': len(articles),
    }

    return render(request, 'storefront/news.html', context)

def news_detail(request, article_id):
    """
    Display a single news article with full content.
    """
    supabase = get_supabase_client()

    try:
        # Fetch article with author information
        response = supabase.table('news_articles').select('*, news_authors(*)').eq('id', article_id).execute()

        if not response.data:
            raise Http404("News article not found")

        article = response.data[0]

        # Increment view count
        try:
            supabase.table('news_articles').update({
                'view_count': article.get('view_count', 0) + 1
            }).eq('id', article_id).execute()
        except Exception as e:
            logger.warning(f"Could not update view count: {e}")

        # Fetch related articles (same category, excluding current)
        try:
            related_response = supabase.table('news_articles').select('id, title, image_url, published_at, read_time_minutes').eq('category', article.get('category')).neq('id', article_id).order('published_at', desc=True).limit(3).execute()
            related_articles = related_response.data or []
        except Exception as e:
            logger.error(f"Error fetching related articles: {e}")
            related_articles = []

        # Fetch comments
        try:
            comments_response = supabase.table('news_comments').select('*, news_authors(name, avatar_url)').eq('article_id', article_id).order('created_at', desc=True).execute()
            comments = comments_response.data or []
        except Exception as e:
            logger.error(f"Error fetching comments: {e}")
            comments = []

        context = {
            'article': article,
            'related_articles': related_articles,
            'comments': comments,
            'comment_count': len(comments),
        }

        return render(request, 'storefront/news_detail.html', context)

    except Exception as e:
        logger.error(f"Error fetching news article {article_id}: {e}")
        raise Http404("News article not found")