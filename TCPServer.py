# TCPServer.py

import json
import re
import asyncio
import aiofiles
from datetime import datetime
from os import path

from constants import HOST, PORT, BUFFER_SIZE


USER_FILE = 'users.json'


class UserLog:
    def __init__(self, req, res, date):
        self.req = req
        self.res = res
        self.date = date
    
    def display(self, username, addr):
        print(f'\nUsername \'{username}\' with address {addr!r} sent a request')
        print(f'Request:  {self.req}')
        print(f'Response: {self.res}')
        print(f'Date:\t  {self.date}\n')

    def toJSON(self):
        return json.dumps(self, default=lambda o: vars(o), sort_keys=True)


def parse_req(req):
    pattern = '\d+\s*[-\+\*\/]\s*\d+'
    if not re.match(pattern, req):
        raise ValueError('Invalid request')

    if '+' in req:
        buffer = req.split('+')
        buffer = [int(val, 10) for val in buffer]
        return buffer[0] + buffer[1]
    elif '-' in req:
        buffer = req.split('-')
        buffer = [int(val, 10) for val in buffer]
        return buffer[0] - buffer[1]
    elif '*' in req:
        buffer = req.split('*')
        buffer = [int(val, 10) for val in buffer]
        return buffer[0] * buffer[1]
    elif '/' in req:
        buffer = req.split('/')
        buffer = [int(val, 10) for val in buffer]
        return buffer[0] / buffer[1]
    else:
        raise ValueError('Invalid request')


def save_record(cache, username, addr, req, res):
    date = datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')
    user_log = UserLog(req, res, date)
    user_log.display(username, addr)
    cache.append(user_log.toJSON())


async def handle_client(reader, writer):
    # prompt the client for username
    writer.write(('Server message: Please enter your username.').encode('utf8'))

    # wait for the username
    username = (await reader.read(BUFFER_SIZE)).decode('utf8').strip()

    # if the database file doesn't exist, create one
    if not path.exists(USER_FILE):
        async with aiofiles.open(USER_FILE, mode='w+') as f:
            await f.write('')

    cache = []
    
    addr = writer.get_extra_info('peername')
    save_record(cache, username, addr, 'Connection establishment', 'OK')

    # prompt the client on how to use the calculation server
    writer.write((f'Server message: {username} connected successfully!\n\nYou can now send basic math calculations requests for two possitive integers.\nThe request should look like:\n\tx <math_operation> y\neg. 5 + 6, 8 / 2, 9 * 12, 7 - 3\nYou can terminate the connection by typing \'quit\'.\n').encode('utf8'))

    while True:
        # wait for the client's request
        request = (await reader.read(BUFFER_SIZE)).decode('utf8')

        # terminating connection request
        if request.lower() == 'quit':
            writer.write(('Server message: OK').encode('utf8'))
            break
            
        try:
            # parse client's request
            # if request is valid, send back the result
            response = parse_req(request)
            writer.write((f'Server message: {request} = {response}').encode('utf8'))
        except ValueError as err:
            # if request is invalid, send back an ERROR message
            response = str(err)
            writer.write((f'Server message: {err}').encode('utf8'))
            
        save_record(cache, username, addr, request, response)
        await writer.drain()
    writer.close()

    save_record(cache, username, addr, 'Connection termination', 'OK')
    async with aiofiles.open(USER_FILE, mode='r') as f:
        contents = await f.read()
        if len(contents) > 0:
            db = json.loads(contents)
        else:
            db = {}
    if username in db:
        db[username].append(cache)
    else:
        db[username] = cache
    async with aiofiles.open(USER_FILE, mode='w') as f:
        await f.write(json.dumps(db))



async def main():
    # start server
    server = await asyncio.start_server(handle_client, HOST, PORT)

    # display info of the server
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n[!] Keyboard Interrupted!')
        print('Server shutting down...')
