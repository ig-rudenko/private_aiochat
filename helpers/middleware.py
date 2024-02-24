from aiohttp_session import get_session
from aiohttp_session import session_middleware
from redis.asyncio import Redis
from aiohttp_session.redis_storage import RedisStorage

from settings import REDIS_PORT, REDIS_HOST


# Декоратор для добавления "user" атрибута в параметр "request"
async def request_user_middleware(app, handler):
    async def middleware(request):
        request.session = await get_session(request) # Получаем сессию для текущего запроса
        request.user = request.session.get("user")  # Из сессии вытягиваем имя пользователя

        return await handler(request)

    return middleware


# Сессии пользователей хранятся в Redis

redis_pool = Redis(host=REDIS_HOST, port=REDIS_PORT)  # Подключение к Redis


# Промежуточное программное обеспечение
middlewares = [
    session_middleware(RedisStorage(redis_pool)),
    request_user_middleware,
]
