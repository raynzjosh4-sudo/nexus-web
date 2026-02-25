def breadcrumb_path(request):
    """Provide a simple breadcrumb string derived from request.path.

    Returns a context variable `breadcrumb_path` containing the path without
    a leading slash and with path separators replaced by ` > `, e.g.
    '/about/team/' -> 'about > team'. This keeps template logic simple
    and avoids using non-standard template filters.
    """
    path = getattr(request, 'path', '') or ''
    # Strip leading/trailing slashes and replace internal slashes with ' > '
    cleaned = path.strip('/')
    if cleaned:
        return {'breadcrumb_path': cleaned.replace('/', ' > ')}
    return {'breadcrumb_path': ''}
