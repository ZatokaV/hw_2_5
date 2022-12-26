import asyncio
import logging
from datetime import datetime

import names
import websockets
from aiopath import AsyncPath
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from exchange import exchange

logging.basicConfig(level=logging.INFO)
LOGFILE = 'logs.txt'


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def send_exchange(self, message, ):
        if message == 'exchange':
            rate = await exchange()
            await self.send_to_clients(f"{'exchange'}: {rate}")
            log = f'{datetime.now()} Called exchange rate for today \n'
            await write_log(log)
        if message.startswith('exchange') and message != 'exchange':
            days: int = message[-1]
            rate = await exchange(days)
            await self.send_to_clients(f"{'exchange'}: {rate}")
            log = f'{datetime.now()} Called exchange rate for {days} days \n'
            await write_log(log)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            await self.send_to_clients(f"{ws.name}: {message}")
            if message.startswith('exchange'):
                await self.send_exchange(message)


async def logging_check():
    log_file = AsyncPath(LOGFILE)
    if await log_file.exists():
        print('logs file ready')
    else:
        await log_file.touch()


async def write_log(log):
    with open(LOGFILE, 'a') as logfile:
        logfile.write(log)


async def serv():
    await logging_check()
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(serv())
