from aiohttp_session import get_session
import aioredis
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage


# Декоратор для добавления "user" атрибута в параметр "request"

async def request_user_middleware(app, handler):
    async def middleware(request):
        request.session = await get_session(request)  # Получаем сессию для текущего запроса
        request.user = None
        username = request.session.get('user')  # Из сессии вытягиваем имя пользователя
        if username is not None:
            request.user = username  # Устанавливаем атрибут пользователя

        return await handler(request)
    return middleware


# Сессии пользователей хранятся в Redis

redis_pool = aioredis.Redis()  # Подключение к Redis


# Промежуточное программное обеспечение
middlewares = [
    session_middleware(RedisStorage(redis_pool)),
    request_user_middleware
]
