from aiohttp import web
from index import views

routes = [
    web.get('/', views.Index, name='index')
]
