from aiohttp import web
from chat import views

routes = [
    web.get('/', views.Index, name='index'),
    web.route('*', '/chat/rooms', views.CreateRoom, name='create_room'),
    web.route('get', '/chat/rooms/{slug}', views.ChatRoom, name='room'),
    web.route('get', '/ws/{slug}', views.WebSocket, name='ws'),
]
