import time

from aiohttp import web
import aiohttp_jinja2
from helpers.decorators import anonymous_required, login_required
from helpers.tools import redirect


class Register(web.View):
    @anonymous_required
    @aiohttp_jinja2.template("accounts/register.html")
    async def get(self):
        """Просто отдаем шаблон, для ввода имени для регистрации"""
        return {}

    @anonymous_required
    @aiohttp_jinja2.template("accounts/register.html")
    async def post(self):
        """Создаем пользователя"""
        data = await self.request.post()
        username = data.get("username")
        # Проверяем имя пользователя и возвращаем результат

        # Если имя не прошло проверку, либо пользователь с таким именем уже имеется в app.users, то
        if not await self.username_is_valid(username) or self.request.app.users.get(username, None):
            # Перенаправляем на страницу регистрации снова
            return {"error": "Неверный пользователь"}

        # Если имя пользователя верное и его еще нет на сайте, то создаем запись о нем в глобальной переменной
        self.request.app.users[username] = {"active": True}

        # Создаем сессию для этого пользователя
        self.login(username)

    @staticmethod
    async def username_is_valid(username: str) -> bool:
        """Проверяем введенное имя пользователя"""
        return username and len(username) >= 4  # Имя должно быть не менее 4 символов

    def login(self, username):
        """Создаем на основе имени пользователя запись сессии в Redis"""

        self.request.session["user"] = username  # Добавляем поле имени
        self.request.session["time"] = time.time()  # Добавляем поле текущего времени
        redirect(self.request, "index")  # Перенаправляем на главную


class LogOut(web.View):
    @login_required
    async def get(self):
        # Вытягиваем запись имени пользователя из сессии (из Redis) и удаляем её
        # И также по этому имени удаляем запись о пользователе в глобальной переменной app.users
        self.request.app.users.pop(self.request.session.pop("user", None), None)
        redirect(self.request, "index")
