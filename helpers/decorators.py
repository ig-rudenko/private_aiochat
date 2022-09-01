from helpers.tools import redirect


def login_required(func):
    """Только авторизованные пользователи"""
    async def wrapped(self, *args, **kwargs):
        # Если пользователь НЕ существует, то перенаправляем на страницу регистрации
        if self.request.user is None:
            redirect(self.request, 'register')
        return await func(self, *args, **kwargs)
    return wrapped


def anonymous_required(func):
    """Только НЕ авторизованные пользователи"""
    async def wrapped(self, *args, **kwargs):
        # Если пользователь существует, то перенаправляем на страницу регистрации
        if self.request.user is not None:
            redirect(self.request, 'index')
        return await func(self, *args, **kwargs)
    return wrapped
