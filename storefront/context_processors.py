
from django.conf import settings


def login_prompt(request):
    """Context processor that indicates whether we should show the login/signup prompt.

    The prompt is only shown for anonymous visitors, and only once per session.
    Once the banner is displayed (or dismissed) the front end should call
    `/login_prompt_seen/` to mark the session and prevent it from reappearing.
    """
    show = False
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        if not request.session.get('seen_login_prompt', False):
            show = True
    return {'show_login_prompt': show}
