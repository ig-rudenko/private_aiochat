from aiohttp_session import get_session
import aioredis
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage


async def request_user_middleware(app, handler):
    async def middleware(request):
        request.session = await get_session(request)
        request.user = None
        username = request.session.get('user')
        if username is not None:
            request.user = username

        return await handler(request)
    return middleware


redis_pool = aioredis.Redis()

middlewares = [
    session_middleware(RedisStorage(redis_pool)),
    request_user_middleware
]
