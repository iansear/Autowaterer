import asyncio
import threading

from .classes.relay import Relay

PUMP_RELAY = Relay(12, False)
PUMP_LOCK = threading.Lock()
WATER_SECONDS = 10


async def water_plants():
    # PUMP_LOCK is acquired by the caller and released here, so that the
    # check and the claim happen in one atomic step in the request handler.
    try:
        print("Turning on the pump!")
        PUMP_RELAY.on()
        await asyncio.sleep(WATER_SECONDS)
    finally:
        PUMP_RELAY.off()
        PUMP_LOCK.release()
        print("Plants watered!")
