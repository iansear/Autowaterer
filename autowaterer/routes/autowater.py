from quart import Blueprint, current_app, render_template, request
from ..tasks import tasks
from datetime import datetime
from ..classes.pump import Pump

bp = Blueprint('autowater', __name__)
water_pump_1 = Pump(12, 1.25)

def get_schedule():
    active_tasks = []
    
    # Safely access the internal tasks storage dictionary
    for task_id, task in tasks._tasks.items():
        active_tasks.append({
            "task_id": task_id,
            "function_name": task.func.__name__,
            # The schedule attribute contains information about the interval or cron syntax
            "schedule": str(task.schedule)  
        })
    return active_tasks

def time_to_cron(time_str: str) -> str:
    """
    Converts 'HH:MM' string to a daily cron expression 'M H * * *'
    Example: '14:30' -> '30 14 * * *'
    Example: '09:05' -> '5 9 * * *'
    """
    try:
        # Parse the input string safely to validate format
        parsed_time = datetime.strptime(time_str.strip(), "%H:%M")
        
        # Strip leading zeros for cleaner cron syntax (optional, but standard)
        minute = parsed_time.minute
        hour = parsed_time.hour
        
        return f"{minute} {hour} * * *"
    except ValueError:
        raise ValueError("Invalid time format. Please use 'HH:MM' (24-hour format).")

@bp.route('/')
async def index():
    return await render_template('water.html', schedule=get_schedule())

@bp.route('/schedule-water', methods=['POST'])
async def schedule_water():
    time = request.form.get('time')
    quantity = request.form.get('quantity')
    if not time or not quantity:
        return "Time and quantity are required!", 400
    print(f"Scheduling water for {time} at {quantity} ml")
    cron_time = time_to_cron(time)
    tasks.schedule_cron(water_pump_1.test_water_pump, cron_time, args=(quantity), task_id='water_cron_test')
    return await render_template('water.html', schedule=get_schedule())

# Test routes for the pump
@bp.route('/water', methods=['POST'])
async def water():
    if water_pump_1.is_running():
        return "Pump is already running!", 400
    current_app.add_background_task(water_pump_1.run_water_pump)
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
