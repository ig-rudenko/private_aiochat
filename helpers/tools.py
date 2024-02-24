from aiohttp import web


def redirect(request, router_name, *, permanent=False, **kwargs):
    """Redirect to given URL name"""
    url = request.app.router[router_name].url_for(**kwargs)
    if permanent:
        raise web.HTTPMovedPermanently(url)
    raise web.HTTPFound(url)
