import datetime
import aiohttp_jinja2
from aiohttp import web

from helpers.decorators import login_required
from helpers.tools import redirect


class CreateRoom(web.View):

    @login_required
    @aiohttp_jinja2.template('chat/rooms.html')
    def get(self):
        """Создание комнат"""
        pass

    @login_required
    async def post(self):
        """Создание комнаты"""

        self.roomname = await self.is_valid()  # Проверяем ввод пользователя и возвращаем результат
        if not self.roomname:  # Если имя комнаты было неверным
            redirect(self.request, 'create_room')

        chat = self.request.app.chats  # Укорачиваем

        # Если в комнате уже есть 2 пользователя, то нельзя к ней подключиться, перенаправляем на создание другой
        if chat.get(self.roomname) and len(chat[self.roomname]) >= 2:
            redirect(self.request, 'create_room')

        # Первое подключение
        elif not chat.get(self.roomname):  # Комнаты еще нет
            chat[self.roomname] = {
                self.request.user: {
                    'active': True
                }
            }

        # Второе подключение
        else:

            # Когда пользователь подключается к комнате, где уже есть кто-то, то формируем сообщение,
            # которое будет отправлено в чат, что данный пользователь подключился
            message = {
                'text': '< Подключился >',
                'created_at': datetime.datetime.now().isoformat(),
                'user': self.request.user
            }

            await self.broadcast(message)  # Отправляем в комнату сообщение

            # Подключаем пользователя в комнату
            chat[self.roomname][self.request.user] = {
                'active': True
            }

        redirect(self.request, 'room', slug=self.roomname)  # Переходим в комнату

    async def is_valid(self):
        data = await self.request.post()  # Вытягиваем пользовательские данные
        roomname = data.get('roomname', '').lower()
        return roomname

    async def broadcast(self, message):
        """Отправка сообщения в комнату"""
        clients_data = self.request.app.chats[self.roomname].values()
        print(clients_data)
        for client in clients_data:
            await client['ws'].send_json(message)  # Отправляем на веб сокет пользователя в данной комнате сообщение


class ChatRoom(web.View):
    """Показываем комнату"""

    @login_required
    @aiohttp_jinja2.template('chat/chat.html')
    def get(self):

        # URL - /chat/room/room_name
        # self.request.match_info['slug'] == 'room_name'

        room = self.request.match_info['slug'].lower()
        return {
            'room': room
        }


class WebSocket(web.View):
    """Обработка веб сокета"""

    async def get(self):

        # URL - /chat/ws/room_name
        # self.request.match_info['slug'] == 'room_name'

        self.room = self.request.match_info['slug'].lower()
        username: str = self.request.user
        app = self.request.app
        app.chats: dict

        ws = web.WebSocketResponse()  # Обработка веб-сокетов
        await ws.prepare(self.request)

        # Если комната не существует или в комнате нет пользователя, то перенаправляем
        if not app.chats.get(self.room) or not app.chats[self.room].get(username):
            redirect(self.request, 'create_room')

        # В глобальную переменную chats для текущего пользователя добавляем его веб сокет
        app.chats[self.room][username]['ws'] = ws

        # Цикл приема новых сообщений
        async for msg in ws:

            # Если тип сообщения это текст
            if msg.type == web.WSMsgType.text:

                # Если пользователь отправил "/close", то прерываем подключение всех пользователей в комнате
                if msg.data == '/close':
                    chats = self.request.app.chats[self.room].values()  # Данные комнаты

                    # Список веб сокетов пользователей в комнате
                    web_sockets = [client_data['ws'] for client_data in chats]

                    for w in web_sockets:  # по очереди каждый веб сокет
                        await w.close()  # Отключаем
                    break  # Прерываем цикл приема новых сообщений

                # В другом случае обрабатываем сообщение
                else:

                    # msg.data - текст сообщения
                    text = msg.data.strip()

                    message = {
                        'text': text,
                        'created_at': datetime.datetime.now().isoformat(),
                        'user': self.request.user
                    }

                    await self.broadcast(message)  # Отправляем сообщение в комнату

            elif msg.type == web.WSMsgType.error:
                print('Error')

        await self.disconnect(username, ws)  # Отключаем пользователя от комнаты

        return ws

    async def broadcast(self, message):
        """Отправляем сообщение в комнату"""
        chats = self.request.app.chats[self.room].values()  # Список пользовательских данных
        print(chats)
        for peer in chats:
            await peer['ws'].send_json(message)  # Отправляем на веб сокет пользователя в данной комнате сообщение

    async def disconnect(self, username, socket):
        """Отключаем пользователя от комнаты"""
        self.request.app.chats[self.room].pop(username, None)
        if not socket.closed:  # Если соединение еще не разорвано
            await socket.close()

        if not self.request.app.chats[self.room]:  # Если в комнате больше нет пользователей
            self.request.app.chats.pop(self.room)  # То удаляем комнату


class Index(web.View):
    """Домашняя страница"""

    @aiohttp_jinja2.template('index.html')
    def get(self):
        pass
