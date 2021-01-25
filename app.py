import os, sys
import asyncio
import platform
from datetime import datetime
from typing import Callable, Any

from aioconsole import ainput
from bleak import BleakClient, discover

PETTUTOR_UUID = "B0E6A4BF-CCCC-FFFF-330C-0000000000F0"
FEED_CHARACTERISTIC = "B0E6A4BF-CCCC-FFFF-330C-0000000000F1"

selected_device = []


class Connection:

    client: BleakClient = None

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        feed_characteristic: str,
    ):
        self.loop = loop
        self.read_characteristic = feed_characteristic
        self.write_characteristic = feed_characteristic

        self.last_packet_time = datetime.now()
        self.connected = False
        self.connected_device = None

    def on_disconnect(self, client: BleakClient):
        self.connected = False
        # Put code here to handle what happens on disconnet.
        print(f"Disconnected from {self.connected_device.name}!")

    async def cleanup(self):
        if self.client:
            await self.client.disconnect()

    async def manager(self):
        print("Starting connection manager.")
        while True:
            if self.client:
                await self.connect()
            else:
                await self.select_device()
                await asyncio.sleep(15.0, loop=loop)

    async def connect(self):
        if self.connected:
            return
        try:
            await self.client.connect()
            self.connected = await self.client.is_connected()
            if self.connected:
                print(f"Connected to {self.connected_device.name}")
                self.client.set_disconnected_callback(self.on_disconnect)
                while True:
                    if not self.connected:
                        break
                    await asyncio.sleep(3.0, loop=loop)
            else:
                print(f"Failed to connect to {self.connected_device.name}")
        except Exception as e:
            print(e)

    async def select_device(self):
        response = -1
        pettutor_device = None
        print("Bluetooh LE hardware warming up...")
        while pettutor_device is None:
            await asyncio.sleep(2.0, loop=loop)  # Wait for BLE to initialize.
            devices = await discover()

            print("\nSearching for PetTutor...")
            for device in devices:
                if device.name == "PTFeeder":
                    print(f"Found PetTutor: '{device}'\n")
                    pettutor_device = device
                    break
            else:
                print("Couldn't find PetTutor. Waiting...")
                continue
            break

        print(f"Connecting to {pettutor_device.name}")
        self.connected_device = pettutor_device
        self.client = BleakClient(pettutor_device.address, loop=self.loop)


#############
# Loops
#############
async def user_console_manager(connection: Connection):
    while True:
        if connection.client and connection.connected:
            input_str = await ainput("Press any key to feed ...")
            bytes_to_send = bytearray(0)
            await connection.client.write_gatt_char(FEED_CHARACTERISTIC, bytes_to_send)
            print(f"Sent feed instruction.")
        else:
            await asyncio.sleep(2.0, loop=loop)


async def main():
    while True:
        # YOUR APP CODE WOULD GO HERE.
        await asyncio.sleep(5)


if __name__ == "__main__":

    # Create the event loop.
    loop = asyncio.get_event_loop()

    connection = Connection(loop, FEED_CHARACTERISTIC)
    try:
        asyncio.ensure_future(connection.manager())
        asyncio.ensure_future(user_console_manager(connection))
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        print("User stopped program.")
    finally:
        print("Disconnecting...")
        loop.run_until_complete(connection.cleanup())
