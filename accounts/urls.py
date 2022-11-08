from aiohttp import web
from accounts import views as acc_views

routes = [
    web.route("*", "/register", acc_views.Register, name="register"),
    web.route("*", "/logout", acc_views.LogOut, name="logout"),
]
