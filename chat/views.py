import datetime
import re
import aiohttp_jinja2

from textwrap import dedent
from aiohttp import web

from helpers.decorators import login_required
from helpers.tools import redirect, add_message, get_object_or_404


class CreateRoom(web.View):

    """ Create new chat room """

    @login_required
    @aiohttp_jinja2.template('chat/rooms.html')
    async def get(self):
        return {'chat_rooms': []}

    @login_required
    async def post(self):
        """ Check is roomname unique and create new User """
        roomname = await self.is_valid()
        if not roomname:
            redirect(self.request, 'create_room')

        chat = self.request.app.chats

        if chat.get(roomname) and len(chat[roomname]) > 1:
            redirect(self.request, 'create_room')

        elif not chat.get(roomname):
            chat[roomname] = {
                self.request.user: {
                    'active': True
                }
            }
        else:
            chat[roomname][self.request.user] = {
                'active': True
            }

        redirect(self.request, 'room', slug=roomname)

    async def is_valid(self):
        """ Get roomname from post data, and check is correct """
        data = await self.request.post()
        roomname = data.get('roomname', '').lower()
        return roomname


class ChatRoom(web.View):

    """ Get room by slug display messages in this Room """

    @login_required
    @aiohttp_jinja2.template('chat/chat.html')
    async def get(self):
        room = self.request.match_info['slug'].lower()
        return {
            'room': {'name': room},
            'chat_rooms': [{'name': room}],
            'room_messages': []
        }


class WebSocket(web.View):

    """ Process WS connections """

    async def get(self):
        self.room = self.request.match_info['slug'].lower()
        user = self.request.user
        app = self.request.app

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        app.chats[self.room][self.request.user]['ws'] = ws

        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                if msg.data == 'close':
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

        await self.disconnect(user, ws)
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

