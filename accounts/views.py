import re
from time import time

import aiohttp_jinja2
from aiohttp import web

from helpers.tools import redirect
from helpers.decorators import anonymous_required, login_required


class LogIn(web.View):

    """ Simple Login user by username """

    template_name = 'accounts/login.html'

    @anonymous_required
    @aiohttp_jinja2.template(template_name)
    async def get(self):
        return {}

    @anonymous_required
    async def post(self):
        """ Check username and login """
        username = await self.is_valid()
        if not username:
            redirect(self.request, 'login')
        self.login_user(username)
        redirect(self.request, 'login')

    def login_user(self, user):
        """ Put user to session and redirect to Index """
        self.request.session['user'] = str(user)
        self.request.session['time'] = time()
        redirect(self.request, 'index')

    async def is_valid(self):
        """ Get username from post data, and check is correct """
        data = await self.request.post()
        username = data.get('username', '').lower()
        if not re.match(r'^[a-z]\w{0,9}$', username):
            return False
        return username


class LogOut(web.View):

    """ Remove current user from session """

    @login_required
    async def get(self):
        username = self.request.session.pop('user')
        # self.request.app.users.pop(username)
        redirect(self.request, 'index')


class Register(LogIn):

    """ Create new user in db """

    template_name = 'accounts/register.html'

    @anonymous_required
    @aiohttp_jinja2.template(template_name)
    async def get(self):
        return {}

    @anonymous_required
    async def post(self):
        """ Check is username unique and create new User """
        username = await self.is_valid()
        if not username:
            redirect(self.request, 'register')
        self.request.users[username] = {
            'active': True
        }
        self.login_user(username)
