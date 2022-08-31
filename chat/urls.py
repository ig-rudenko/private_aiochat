from aiohttp import web
from chat import views as forum_views

routes = [
    web.route('*', '/chat/rooms', forum_views.CreateRoom, name='create_room'),
    web.route('get', '/chat/rooms/{slug}', forum_views.ChatRoom, name='room'),
    web.route('get', '/ws/{slug}', forum_views.WebSocket, name='ws'),
]
