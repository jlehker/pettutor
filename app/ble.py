import asyncio

from bleak import BleakClient, discover


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
                await asyncio.sleep(15.0, loop=self.loop)

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
                    await asyncio.sleep(3.0, loop=self.loop)
            else:
                print(f"Failed to connect to {self.connected_device.name}")
        except Exception as e:
            print(e)

    async def select_device(self):
        pettutor_device = None
        print("Bluetooh LE hardware warming up...")
        while pettutor_device is None:
            await asyncio.sleep(2.0, loop=self.loop)  # Wait for BLE to initialize.
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
