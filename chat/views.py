import datetime
from aiohttp_jinja2 import template
from aiohttp import web, WSMessage

from helpers.decorators import login_required
from helpers.tools import redirect


class CreateRoom(web.View):
    @login_required
    @template("chat/rooms.html")
    async def get(self):
        """Создание комнат"""
        return {}

    @login_required
    async def post(self):
        """Создание комнаты"""
        room_name = await self.get_valid_room()

        chats: dict = self.request.app.chats  # Укорачиваем

        # Если в комнате уже есть 2 пользователя, то нельзя к ней подключиться, перенаправляем на создание другой
        if chats.get(room_name) and len(chats[room_name]) >= 2:
            redirect(self.request, "create_room")

        # Первое подключение
        elif not chats.get(room_name):  # Комнаты еще нет
            chats[room_name] = {self.request.user: {"active": True}}

        # Второе подключение
        else:

            # Когда пользователь подключается к комнате, где уже есть кто-то, то формируем сообщение,
            # которое будет отправлено в чат, что данный пользователь подключился
            message = {
                "text": "< Подключился >",
                "created_at": datetime.datetime.now().isoformat(),
                "user": self.request.user,
            }

            await self.broadcast(message, room_name)  # Отправляем в комнату сообщение

            # Подключаем пользователя в комнату
            chats[room_name][self.request.user] = {"active": True}

        redirect(self.request, "room", slug=room_name)  # Переходим в комнату

    async def get_valid_room(self) -> str:
        data = await self.request.post()  # Вытягиваем пользовательские данные
        # Проверяем ввод пользователя и возвращаем результат
        room_name = str(data.get("roomname", "")).lower()
        if not room_name:  # Если имя комнаты было неверным
            redirect(self.request, "create_room")
        return room_name

    async def broadcast(self, message: dict, room_name: str):
        """Отправка сообщения в комнату"""
        clients_data = self.request.app.chats[room_name].values()
        for client in clients_data:
            # Отправляем на веб сокет пользователя в данной комнате сообщение
            await client["ws"].send_json(message)


class ChatRoom(web.View):
    """Показываем комнату"""

    @login_required
    @template("chat/chat.html")
    async def get(self):

        # URL - /chat/room/room_name
        # self.request.match_info['slug'] == 'room_name'

        room = self.request.match_info["slug"].lower()
        return {"room": room}


class WebSocket(web.View):
    """Обработка веб сокета"""

    async def get(self):

        # URL - /chat/ws/room_name
        # self.request.match_info['slug'] == 'room_name'

        room_name = self.request.match_info["slug"].lower()
        username: str = self.request.user
        all_chats: dict = self.request.app.chats

        # Если комната не существует или в комнате нет пользователя, то перенаправляем
        if not all_chats.get(room_name) or not all_chats[room_name].get(username):
            redirect(self.request, "create_room")

        ws = web.WebSocketResponse()  # Обработка веб-сокетов
        await ws.prepare(self.request)

        # В глобальную переменную chats для текущего пользователя добавляем его веб сокет
        all_chats[room_name][username]["ws"] = ws

        # Цикл приема новых сообщений
        async for msg in ws:
            msg: WSMessage

            # Если тип сообщения это текст
            if msg.type == web.WSMsgType.text:
                # msg.data - текст сообщения
                text = msg.data.strip()

                # Если пользователь отправил текст `/close`, то прерываем подключение всех пользователей в комнате
                if text == "/close":
                    await self.close_room(room_name)
                    break  # Прерываем цикл приема новых сообщений

                # В другом случае обрабатываем сообщение
                message = {
                    "text": text,
                    "created_at": datetime.datetime.now().isoformat(),
                    "user": self.request.user,
                }
                await self.broadcast(message, room_name)  # Отправляем сообщение в комнату

            elif msg.type == web.WSMsgType.error:
                print("Error")

        await self.disconnect(username, ws, room_name)  # Отключаем пользователя от комнаты

        return ws

    async def close_room(self, room_name: str) -> None:
        room_users = self.request.app.chats[room_name].values()  # Данные комнаты
        for user in room_users:
            if not user["ws"].closed:
                await user["ws"].close()

    async def broadcast(self, message: dict, room_name: str) -> None:
        """Отправляем сообщение всем в комнату"""
        # Список пользовательских данных
        chats = self.request.app.chats[room_name].values()
        for peer in chats:
            # Отправляем на веб сокет пользователя в данной комнате сообщение
            await peer["ws"].send_json(message)

    async def disconnect(self, username: str, socket: web.WebSocketResponse, room_name: str) -> None:
        """Отключаем пользователя от комнаты"""
        self.request.app.chats[room_name].pop(username, None)
        if not socket.closed:  # Если соединение еще не разорвано
            await socket.close()

        if not self.request.app.chats[room_name]:
            # Если в комнате больше нет пользователей
            self.request.app.chats.pop(room_name)  # То удаляем комнату


class Index(web.View):
    """Домашняя страница"""

    @template("index.html")
    async def get(self):
        return {}
