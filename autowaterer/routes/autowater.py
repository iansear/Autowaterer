import time

from quart import Blueprint, current_app

from ..pump import PUMP_LOCK, water_plants

bp = Blueprint('autowater', __name__)


@bp.route('/')
async def index():
    return "I love you my darling!"


@bp.route('/water')
async def water():
    if not PUMP_LOCK.acquire(blocking=False):
        return "Pump is already running, try again in a moment.", 409

    print("Watering the plants!")
    current_app.add_background_task(water_plants)
    return f"Watering started at {time.strftime('%Y-%m-%d %H:%M:%S')}", 202
