import asyncio
import threading

from .classes.relay import Relay

PUMP_RELAY = Relay(12, False)
PUMP_LOCK = threading.Lock()
WATER_SECONDS = 10


def try_start_watering(app):
    """Start a watering run, or return False if one is already in progress."""
    if not PUMP_LOCK.acquire(blocking=False):
        return False

    app.add_background_task(_water_plants)
    return True


async def _water_plants():
    # Releases the lock claimed by try_start_watering, so it must not be
    # started any other way.
    try:
        print("Turning on the pump!")
        PUMP_RELAY.on()
        await asyncio.sleep(WATER_SECONDS)
    finally:
        PUMP_RELAY.off()
        PUMP_LOCK.release()
        print("Plants watered!")
