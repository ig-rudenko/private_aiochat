from aiohttp import web


def redirect(request, router_name, *, permanent=False, **kwargs):
    """Redirect to given URL name"""
    print(request.app.router["index"])
    url = request.app.router[router_name].url_for(**kwargs)
    print(url)
    if permanent:
        raise web.HTTPMovedPermanently(url)
    raise web.HTTPFound(url)
