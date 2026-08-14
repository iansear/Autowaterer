import time

from quart import Blueprint, current_app, render_template

from ..pump import try_start_watering, turn_on_pump, turn_off_pump

bp = Blueprint('autowater', __name__)

start_time = None
end_time = None

@bp.route('/')
async def index():
    return await render_template('water.html')


@bp.route('/water', methods=['POST'])
async def water():
    if not try_start_watering():
        return "Pump is already running, try again in a moment.", 409

    print("Watering the plants!")
    return f"Watering started at {time.strftime('%Y-%m-%d %H:%M:%S')}", 202

@bp.route('/turn-on-pump', methods=['POST'])
async def turn_on_pump():
    print('Turning on pump')
    if not await turn_on_pump():
        print('Failed to turn on pump')
        return 'Failed to turn on pump', 500
    start_time = time.time()
    return f'Pump turned on at {start_time}', 200

@bp.route('/turn-off-pump', methods=['POST'])
async def turn_off_pump():
    print('Turning off pump')
    if not turn_off_pump():
        print('Failed to turn off pump')
        return 'Failed to turn off pump', 500
    end_time = time.time()
    return f'Pump turned off, ran for {end_time - start_time:.2f} seconds', 200
