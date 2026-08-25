import asyncio
import threading

from .classes.relay import Relay

PUMP_RELAY = Relay(12, False)
PUMP_LOCK = threading.Lock()
WATER_SECONDS = 10

#rate is 100ml/80s = 1.25ml/s

# True while the pump is held on manually, so turn_off_pump knows whether the
# lock is ours to release or belongs to a timed watering run.
_manual_hold = False


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

def turn_on_pump():
    """Switch the pump on and hold it on until turn_off_pump is called."""
    global _manual_hold

    if not PUMP_LOCK.acquire(blocking=False):
        return False

    try:
        PUMP_RELAY.on()
        _manual_hold = True
        return True
    except Exception as e:
        print(f'Error turning on pump: {e}')
        PUMP_LOCK.release()
        return False


def turn_off_pump():
    """Switch the pump off. Safe to call at any time, including mid-run."""
    global _manual_hold

    try:
        PUMP_RELAY.off()
        return True
    except Exception as e:
        print(f'Error turning off pump: {e}')
        return False
    finally:
        if _manual_hold:
            _manual_hold = False
            PUMP_LOCK.release()