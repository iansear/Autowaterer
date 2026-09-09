from quart import Blueprint, current_app, flash, render_template, redirect, url_for, request
from datetime import datetime
from ..config.pump_config import WATER_PUMP_1_RUN, water_pump_1
from ..config.schedule_config import scheduler
from ..db import db
from ..db.job import Job

bp = Blueprint('autowater', __name__)

@bp.route('/')
async def index():
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.strftime('%Y-%m-%d %H:%M')
        })
    return await render_template('water.html', schedule=jobs)

@bp.route('/schedule-water', methods=['POST'])
async def schedule_water():
    form = await request.form
    time = form.get('time')
    quantity = form.get('quantity')

    if time and quantity:
        try:
            quantity = float(quantity)
            parsed_time = datetime.strptime(time.strip(), "%H:%M")
            time_label = f'{parsed_time.hour}:{parsed_time.minute:02d}'
            print('parsed_time', parsed_time)
            print('hour', parsed_time.hour)
            print('minute', parsed_time.minute)
            print('time_label', time_label)
            job_name = f'{quantity:g}ml at {time_label}'
            scheduler.add_job(
                water_pump_1.run_water_pump,
                name=job_name,
                trigger='cron',
                hour=parsed_time.hour,
                minute=parsed_time.minute,
                args=[quantity]
            )
            job = Job(
                name=job_name,
                function=WATER_PUMP_1_RUN,
                trigger='cron',
                hour=parsed_time.hour,
                minute=parsed_time.minute,
                args=[quantity]
            )
            async with db.bind.Session() as session:
                async with session.begin():
                    session.add(job)
        except Exception as e:
            print(f"Error scheduling water: {e}")
            flash(f"Error scheduling water: {e}")
    else:
        print('Time and quantity are required!')
        flash('Time and quantity are required!')
    return redirect(url_for('autowater.index'))

# Test routes for the pump
@bp.route('/water', methods=['POST'])
async def water():
    if water_pump_1.is_running():
        return "Pump is already running!", 400
    test_quantity = 200
    current_app.add_background_task(water_pump_1.run_water_pump, test_quantity)
    return f"Pump test - dispensing {test_quantity}ml", 200

@bp.route('/turn-on-pump', methods=['POST'])
async def turn_on_pump():
    if water_pump_1.is_running():
        return "Pump is already running", 400
    if not water_pump_1.turn_on():
        return "Failed to turn on pump", 500
    return "Turning on pump", 200

@bp.route('/turn-off-pump', methods=['POST'])
async def turn_off_pump():
    if not water_pump_1.turn_off():
        return "Failed to turn off pump", 500
    return "Turning off pump", 200
