import time

from quart import Blueprint, current_app, render_template

from .. import pump

bp = Blueprint('autowater', __name__)

pump_started_at = None


@bp.route('/')
async def index():
    return await render_template('water.html')


@bp.route('/water', methods=['POST'])
async def water():
    if not pump.try_start_watering(current_app):
        return "Pump is already running, try again in a moment.", 409

    print("Watering the plants!")
    return f"Watering started at {time.strftime('%Y-%m-%d %H:%M:%S')}", 202


@bp.route('/turn-on-pump', methods=['POST'])
async def turn_on_pump():
    global pump_started_at

    print('Turning on pump')
    if not pump.turn_on_pump():
        return 'Pump is already running, try again in a moment.', 409

    pump_started_at = time.time()
    return f'Pump turned on at {time.strftime("%Y-%m-%d %H:%M:%S")}', 200


@bp.route('/turn-off-pump', methods=['POST'])
async def turn_off_pump():
    global pump_started_at

    print('Turning off pump')
    if not pump.turn_off_pump():
        return 'Failed to turn off pump', 500

    if pump_started_at is None:
        return 'Pump turned off.', 200

    ran_for = time.time() - pump_started_at
    pump_started_at = None
    return f'Pump turned off, ran for {ran_for:.2f} seconds', 200
