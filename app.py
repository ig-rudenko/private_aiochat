import jinja2
from aiohttp import web
from chat.urls import routes as chat_routes
from accounts.urls import routes as acc_routes
from settings import BASE_DIR
from helpers.middleware import middlewares
import aiohttp_jinja2


if __name__ == '__main__':
    app = web.Application(middlewares=middlewares)

    jinja_env = aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(BASE_DIR / 'templates'),
        context_processors=[aiohttp_jinja2.request_processor],
    )

    app.router.add_routes(chat_routes)
    app.router.add_routes(acc_routes)

    app.chats = {}
    app.users = {}

    app.router.add_static('/static/', BASE_DIR / 'static', name='static')

    web.run_app(app)
