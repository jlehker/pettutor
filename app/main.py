import asyncio

from fastapi import FastAPI

from .ble import Connection
from .constants import FEED_CHARACTERISTIC


app = FastAPI()
loop = asyncio.get_event_loop()
queue = asyncio.Queue()
connection = None

async def user_console_manager(connection: Connection, queue: asyncio.Queue):
    while True:
        if connection.client and connection.connected:
            await queue.get()
            bytes_to_send = bytearray(0)
            await connection.client.write_gatt_char(FEED_CHARACTERISTIC, bytes_to_send)
            print(f"Sent feed instruction.")
        else:
            await asyncio.sleep(2.0, loop=loop)


@app.on_event("startup")
async def startup_event():
    connection = Connection(loop, FEED_CHARACTERISTIC)
    asyncio.ensure_future(connection.manager())
    asyncio.ensure_future(user_console_manager(connection, queue))


@app.on_event("shutdown")
async def shutdown_event():
    print("Disconnecting...")
    loop.run_until_complete(connection.cleanup())


@app.get("/feed")
async def feed():
    if queue is not None:
        queue.put_nowait(0)
    return "done."
