import re
from time import time

import aiohttp_jinja2
from aiohttp import web

from helpers.tools import redirect
from helpers.decorators import anonymous_required, login_required


class LogOut(web.View):
    @login_required
    async def get(self):
        self.request.app.users.pop(
            self.request.session.pop('user', None), None
        )
        redirect(self.request, 'index')


class Register(web.View):

    @anonymous_required
    @aiohttp_jinja2.template('accounts/register.html')
    async def get(self):
        pass

    @anonymous_required
    async def post(self):
        """ Check is username unique and create new User """
        username = await self.is_valid()
        if not username or self.request.app.users.get(username, None):
            redirect(self.request, 'register')

        self.request.app.users[username] = {
            'active': True
        }
        self.login_user(username)

    async def is_valid(self):
        """ Get username from post data, and check is correct """
        data = await self.request.post()
        username = data.get('username', '').lower()
        if not re.match(r'^[a-z]\w{0,9}$', username):
            return False
        return username

    def login_user(self, user):
        """ Put user to session and redirect to Index """
        self.request.session['user'] = str(user)
        self.request.session['time'] = time()
        redirect(self.request, 'index')
