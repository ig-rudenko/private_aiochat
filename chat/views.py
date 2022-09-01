import datetime
import aiohttp_jinja2
from aiohttp import web

from helpers.decorators import login_required
from helpers.tools import redirect


class CreateRoom(web.View):

    """ Create new chat room """

    @login_required
    @aiohttp_jinja2.template('chat/rooms.html')
    async def get(self):
        return {'chat_rooms': []}

    @login_required
    async def post(self):
        """ Check is roomname unique and create new User """
        self.roomname = await self.is_valid()
        if not self.roomname:
            redirect(self.request, 'create_room')

        chat = self.request.app.chats

        if chat.get(self.roomname) and len(chat[self.roomname]) > 1:
            redirect(self.request, 'create_room')

        # Первое подключение
        elif not chat.get(self.roomname):
            chat[self.roomname] = {
                self.request.user: {
                    'active': True
                }
            }

        # Второе подключение
        else:
            message = {
                'text': '< Подключился >',
                'created_at': datetime.datetime.now().isoformat(),
                'user': self.request.user
            }
            await self.broadcast(message)

            chat[self.roomname][self.request.user] = {
                'active': True
            }

        redirect(self.request, 'room', slug=self.roomname)

    async def is_valid(self):
        """ Get roomname from post data, and check is correct """
        data = await self.request.post()
        roomname = data.get('roomname', '').lower()
        return roomname

    async def broadcast(self, message):
        """ Send messages to all in this room """
        chats = self.request.app.chats[self.roomname].values()
        print(chats)
        for peer in chats:
            await peer['ws'].send_json(message)


class ChatRoom(web.View):

    """ Get room by slug display messages in this Room """

    @login_required
    @aiohttp_jinja2.template('chat/chat.html')
    async def get(self):
        room = self.request.match_info['slug'].lower()
        return {
            'room': {'name': room},
            'room_messages': []
        }


class WebSocket(web.View):

    """ Process WS connections """

    async def get(self):
        self.room = self.request.match_info['slug'].lower()
        username: str = self.request.user
        app = self.request.app
        app.chats: dict

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        if not app.chats.get(self.room) or not app.chats[self.room].get(username):
            redirect(self.request, 'create_room')

        app.chats[self.room][username]['ws'] = ws

        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                if msg.data == '/close':
                    await ws.close()
                else:
                    text = msg.data.strip()

                    message = {
                        'text': text,
                        'created_at': datetime.datetime.now().isoformat(),
                        'user': self.request.user
                    }
                    await self.broadcast(message)

            elif msg.type == web.WSMsgType.error:
                app.logger.debug(f'Connection closed with exception {ws.exception()}')

        await self.disconnect(username, ws)
        return ws

    async def broadcast(self, message):
        """ Send messages to all in this room """
        chats = self.request.app.chats[self.room].values()
        print(chats)
        for peer in chats:
            await peer['ws'].send_json(message)

    async def disconnect(self, username, socket):
        """ Close connection and notify broadcast """
        self.request.app.chats[self.room].pop(username, None)
        if not socket.closed:
            await socket.close()
        if not self.request.app.chats[self.room]:
            self.request.app.chats.pop(self.room)


class Index(web.View):
    """ Main page view """

    @aiohttp_jinja2.template('index.html')
    async def get(self):
        print(self.request.app.chats)
        pass
