import time

from quart import Blueprint, current_app, render_template
#from quart_tasks import QuartTasks

from ..classes.pump import Pump

bp = Blueprint('autowater', __name__)

water_pump_1 = Pump(12, 1.25)

@bp.route('/')
async def index():
    return await render_template('water.html')


@bp.route('/water', methods=['POST'])
async def water():
    if water_pump_1.is_running():
        return "Pump is already running!", 400
    current_app.add_background_task(water_pump_1.test_water_pump)
    return "Watering the plants!", 200

@bp.route('/turn-on-pump', methods=['POST'])
async def turn_on_pump():
    if water_pump_1.is_running():
        return "Pump is already running!", 400
    if not water_pump_1.turn_on():
        return "Failed to turn on pump!", 500
    return "Turning on pump!", 200

@bp.route('/turn-off-pump', methods=['POST'])
async def turn_off_pump():
    if not water_pump_1.turn_off():
        return "Failed to turn off pump!", 500
    return "Turning off pump!", 200
