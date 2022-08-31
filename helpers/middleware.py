from aiohttp_session import get_session


async def request_user_middleware(app, handler):
    async def middleware(request):
        request.session = await get_session(request)
        request.user = None
        username = request.session.get('user')
        if username is not None:
            request.user = username

        return await handler(request)
    return middleware

