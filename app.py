import jinja2
from aiohttp import web
from chat.urls import routes as chat_routes
from accounts.urls import routes as acc_routes
from settings import *
from helpers.middleware import middlewares
import aiohttp_jinja2


if __name__ == "__main__":

    # Устанавливаем промежуточное программное обеспечение
    app = web.Application(middlewares=middlewares)

    # Настраиваем папку с шаблонами
    jinja_env = aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(BASE_DIR / "templates"),
        context_processors=[aiohttp_jinja2.request_processor],
    )

    app.router.add_routes(chat_routes)
    app.router.add_routes(acc_routes)

    app.users = {}  # Глобальная переменная для всех активных пользователей
    # {
    #     'username': {
    #         'status': True
    #     }
    # }

    app.chats = {}  # Глобальная переменная - все комнаты с подключенными пользователями
    # {
    #     'room_name': {
    #         'username1': {
    #             'status': True,
    #             'ws': '<WebSocketClass>'
    #         },
    #         'username2': {
    #             'status': True,
    #             'ws': '<WebSocketClass>'  # Активная сессия web socket'а
    #         }
    #     }
    # }

    # Настраиваем статику
    app.router.add_static("/static/", BASE_DIR / "static", name="static")

    # Запускаем приложение
    web.run_app(app, host=HOST, port=PORT)
