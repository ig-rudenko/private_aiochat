import jinja2
from aiohttp import web
from chat.urls import routes as f_routes
from accounts.urls import routes as a_routes
from index.urls import routes as i_routes
from settings import BASE_DIR
from helpers.template_tags import tags
from helpers.middleware import request_user_middleware
import aiohttp_jinja2
import aioredis
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage

redis_pool = aioredis.Redis()

middlewares = [
    session_middleware(RedisStorage(redis_pool)),
    request_user_middleware
]


if __name__ == '__main__':
    app = web.Application(middlewares=middlewares)

    jinja_env = aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(BASE_DIR / 'templates'),
        context_processors=[aiohttp_jinja2.request_processor],
    )

    jinja_env.globals.update(tags)

    app.router.add_routes(f_routes)
    app.router.add_routes(a_routes)
    app.router.add_routes(i_routes)
    app.chats = {}
    app.users = {}

    app.router.add_static('/static/', BASE_DIR / 'static', name='static')

    web.run_app(app)
