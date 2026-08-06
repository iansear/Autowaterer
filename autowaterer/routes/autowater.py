import time

from quart import Blueprint, current_app, render_template

from ..pump import try_start_watering

bp = Blueprint('autowater', __name__)


@bp.route('/')
async def index():
    return await render_template('water.html')


@bp.route('/water')
async def water():
    if not try_start_watering(current_app):
        return "Pump is already running, try again in a moment.", 409

    print("Watering the plants!")
    return f"Watering started at {time.strftime('%Y-%m-%d %H:%M:%S')}", 202
