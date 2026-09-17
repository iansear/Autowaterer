from quart import Blueprint, current_app, flash, render_template, redirect, url_for, request, websocket
from datetime import datetime
import asyncio
import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..classes.pump import Pump as HardwarePump
from ..classes.water_level_sensor import WaterLevelSensor as HardwareWaterLevelSensor
from ..config.pump_config import loaded_pumps
from ..config.water_level_sensor_config import loaded_water_level_sensors
from ..config.schedule_config import scheduler
from ..db import db
from ..db.job import Job
from ..db.pump import Pump
from ..db.water_level_sensor import WaterLevelSensor

JOB_FUNCTION = 'run_water_pump'

bp = Blueprint('autowater', __name__)


async def list_pumps():
    async with db.bind.Session() as session:
        pumps = (await session.scalars(select(Pump))).all()
        return [
            {
                'id': pump.id,
                'name': pump.name,
                'description': pump.description,
                'gpio_pin': pump.gpio_pin,
                'rate': pump.rate,
            }
            for pump in pumps
        ]


async def list_water_level_sensors():
    async with db.bind.Session() as session:
        water_level_sensors = (await session.scalars(select(WaterLevelSensor))).all()
    return [
        {
            'id': sensor_id,
            'name': sensor.name,
            'resevoir_depth': sensor.resevoir_depth,
        }
        for sensor_id, sensor in loaded_water_level_sensors.items()
    ]

@bp.route('/')
async def index():
    return redirect(url_for('autowater.dashboard'))

# Page routes
@bp.route('/dashboard')
async def dashboard():
    jobs = []
    async with db.bind.Session() as session:
        db_jobs = (await session.scalars(select(Job).options(selectinload(Job.pump)))).all()
        for job in db_jobs:
            sched_job = scheduler.get_job(str(job.id))
            next_run = ''
            if sched_job and sched_job.next_run_time:
                next_run = sched_job.next_run_time.strftime('%Y-%m-%d %H:%M')
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': next_run,
                'pump': job.pump.name if job.pump else '',
                'quantity': f'{job.args[0]} ml' if job.args else '',
                'time': f'{job.hour}:{job.minute:02d}',
            })
    pumps = await list_pumps()
    water_level_sensors = await list_water_level_sensors()
    return await render_template(
        'dashboard.html',
        jobs=jobs,
        pumps=pumps,
        water_level_sensors=water_level_sensors,
    )

@bp.route('/schedule')
async def schedule():
    jobs = []
    async with db.bind.Session() as session:
        db_jobs = (await session.scalars(select(Job).options(selectinload(Job.pump)))).all()
        for job in db_jobs:
            sched_job = scheduler.get_job(str(job.id))
            next_run = ''
            if sched_job and sched_job.next_run_time:
                next_run = sched_job.next_run_time.strftime('%Y-%m-%d %H:%M')
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': next_run,
                'pump': job.pump.name if job.pump else '',
                'quantity': job.args[0] if job.args else '',
                'time': f'{job.hour}:{job.minute:02d}',
                'minute': job.minute,
                'created_at': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else '',
            })
    return await render_template('schedule.html', jobs=jobs)

@bp.route('/pumps')
async def pumps():
    return await render_template('pumps.html', pumps=await list_pumps())

@bp.route('/sensors')
async def sensors():
    return await render_template('sensors.html', water_level_sensors=await list_water_level_sensors())

@bp.route('/tests')
async def tests():
    return await render_template('tests.html', pumps=await list_pumps())

# Job routes
@bp.route('/create-job', methods=['GET', 'POST'])
async def create_job():
    pumps = await list_pumps()
    if request.method == 'GET':
        return await render_template('create_job.html', pumps=pumps)

    form = await request.form
    name = (form.get('name') or '').strip()
    pump_id = form.get('pump_id')
    time = form.get('time')
    quantity = form.get('quantity')

    if not (name and pump_id and time and quantity):
        await flash('Name, pump, time, and quantity are required!')
        return await render_template('create_job.html', pumps=pumps)

    try:
        pump_id = int(pump_id)
        quantity = float(quantity)
        if quantity <= 0:
            await flash('Quantity must be greater than 0.')
            return await render_template('create_job.html', pumps=pumps)

        hardware_pump = loaded_pumps.get(pump_id)
        if hardware_pump is None:
            await flash('Unknown pump.')
            return await render_template('create_job.html', pumps=pumps)

        parsed_time = datetime.strptime(time.strip(), "%H:%M")
        job = Job(
            name=name,
            pump_id=pump_id,
            function=JOB_FUNCTION,
            trigger='cron',
            hour=parsed_time.hour,
            minute=parsed_time.minute,
            args=[quantity],
        )
        async with db.bind.Session() as session:
            async with session.begin():
                session.add(job)
                await session.flush()
                scheduler.add_job(
                    hardware_pump.run_water_pump,
                    id=str(job.id),
                    name=job.name,
                    trigger='cron',
                    hour=parsed_time.hour,
                    minute=parsed_time.minute,
                    args=[quantity],
                )
    except Exception as e:
        print(f"Error scheduling water: {e}")
        await flash(f"Error scheduling water: {e}")
        return await render_template('create_job.html', pumps=pumps)

    return redirect(url_for('autowater.schedule'))

@bp.route('/delete-job', methods=['POST'])
async def delete_job():
    form = await request.form
    job_id = form.get('job_id')
    if not job_id:
        await flash('Job id is required!')
        return redirect(url_for('autowater.schedule'))

    sched_job = scheduler.get_job(job_id)
    if sched_job:
        scheduler.remove_job(job_id)

    async with db.bind.Session() as session:
        async with session.begin():
            db_job = None
            if job_id.isdigit():
                db_job = await session.get(Job, int(job_id))
            if db_job is not None:
                await session.delete(db_job)

    return redirect(url_for('autowater.schedule'))

# Pump routes
@bp.route('/create-pump', methods=['GET', 'POST'])
async def create_pump():
    if request.method == 'GET':
        return await render_template('create_pump.html')

    form = await request.form
    name = form.get('name')
    description = form.get('description')
    try:
        gpio_pin = int(form.get('gpio_pin'))
        rate = float(form.get('rate'))
    except (TypeError, ValueError):
        await flash('GPIO pin and rate are required.')
        return await render_template('create_pump.html')

    pump = Pump(name=name, description=description, gpio_pin=gpio_pin, rate=rate)
    try:
        async with db.bind.Session() as session:
            async with session.begin():
                session.add(pump)
                await session.flush()
                loaded_pumps[pump.id] = HardwarePump(gpio_pin, rate)
    except Exception as e:
        print(f'Error creating pump: {e}')
        await flash(f'Error creating pump: {e}')
        return await render_template('create_pump.html')
    return redirect(url_for('autowater.pumps'))

@bp.route('/delete-pump', methods=['POST'])
async def delete_pump():
    form = await request.form
    pump_id = form.get('pump_id')
    if not pump_id:
        await flash('Pump id is required!')
        return redirect(url_for('autowater.pumps'))

    async with db.bind.Session() as session:
        async with session.begin():
            pump = await session.get(Pump, int(pump_id))
            if pump is not None:
                jobs = (await session.scalars(select(Job).where(Job.pump_id == pump.id))).all()
                for job in jobs:
                    if scheduler.get_job(str(job.id)):
                        scheduler.remove_job(str(job.id))
                    await session.delete(job)
                await session.delete(pump)
                hardware_pump = loaded_pumps.pop(int(pump_id), None)
                if hardware_pump is not None:
                    hardware_pump.interrupt()
                    if hardware_pump.is_running():
                        hardware_pump.turn_off()
                    try:
                        hardware_pump.close()
                    except Exception as e:
                        print(f'Error closing pump: {e}')
    return redirect(url_for('autowater.pumps'))

# Water Level Sensor routes
@bp.route('/create-water-level-sensor', methods=['GET', 'POST'])
async def create_water_level_sensor():
    if request.method == 'GET':
        return await render_template('create_water_level_sensor.html')

    form = await request.form
    name = form.get('name')
    trigger_pin = form.get('trigger_pin')
    echo_pin = form.get('echo_pin')

    try:
        trigger_pin = int(trigger_pin)
        echo_pin = int(echo_pin)
    except (TypeError, ValueError):
        await flash('Trigger pin and echo pin are required.')
        return await render_template('create_water_level_sensor.html')

    hardware_water_level_sensor = None
    water_level_sensor = None
    try:
        water_level_sensor = WaterLevelSensor(
            name=name,
            trigger=trigger_pin,
            echo=echo_pin,
            resevoir_depth=0,
        )
        async with db.bind.Session() as session:
            async with session.begin():
                session.add(water_level_sensor)
                await session.flush()
                hardware_water_level_sensor = HardwareWaterLevelSensor(
                    echo=echo_pin,
                    trigger=trigger_pin,
                    id=water_level_sensor.id,
                    name=name,
                    resevoir_depth=200,
                )
                loaded_water_level_sensors[water_level_sensor.id] = hardware_water_level_sensor
                water_level_sensor.resevoir_depth = await asyncio.to_thread(
                    hardware_water_level_sensor.calibrate
                )
    except Exception as e:
        sensor_id = getattr(water_level_sensor, 'id', None)
        if sensor_id is not None:
            loaded_water_level_sensors.pop(sensor_id, None)
        if hardware_water_level_sensor is not None:
            try:
                hardware_water_level_sensor.close()
            except Exception:
                pass
        print(f'Error creating water level sensor: {e}')
        await flash(f'Error creating water level sensor: {e}')
        return await render_template('create_water_level_sensor.html')
    return redirect(url_for('autowater.sensors'))

@bp.route('/delete-water-level-sensor', methods=['POST'])
async def delete_water_level_sensor():
    form = await request.form
    water_level_sensor_id = form.get('water_level_sensor_id')
    if not water_level_sensor_id:
        await flash('Water level sensor id is required!')
        return redirect(url_for('autowater.sensors'))

    async with db.bind.Session() as session:
        async with session.begin():
            water_level_sensor = await session.get(WaterLevelSensor, int(water_level_sensor_id))
            if water_level_sensor is not None:
                await session.delete(water_level_sensor)
                hardware_water_level_sensor = loaded_water_level_sensors.pop(int(water_level_sensor_id), None)
                if hardware_water_level_sensor is not None:
                    try:
                        hardware_water_level_sensor.close()
                    except Exception as e:
                        print(f'Error closing water level sensor: {e}')
    return redirect(url_for('autowater.sensors'))

# Web Socket
async def _wait_for_stop(delay=0.5):
    stop = current_app.extensions.get("stop_serving")
    waiters = [asyncio.create_task(asyncio.sleep(delay))]
    if stop is not None:
        waiters.append(asyncio.create_task(stop.wait()))
    waiters.append(asyncio.create_task(current_app.shutdown_event.wait()))
    done, pending = await asyncio.wait(waiters, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    sleeper, *stoppers = waiters
    return sleeper not in done


@bp.websocket('/pump-status')
async def pump_status():
    try:
        while True:
            statuses = []
            for pump_id, hardware_pump in loaded_pumps.items():
                last_run = hardware_pump.get_last_run()
                if isinstance(last_run, datetime):
                    last_run_text = last_run.strftime('%Y-%m-%d %H:%M:%S')
                elif last_run:
                    last_run_text = str(last_run)
                else:
                    last_run_text = ''
                statuses.append({
                    'id': pump_id,
                    'running': hardware_pump.is_running(),
                    'elapsed': hardware_pump.get_time_elapsed(),
                    'last_run': last_run_text,
                })
            await websocket.send(json.dumps(statuses))
            if await _wait_for_stop():
                return
    except asyncio.CancelledError:
        raise
    except Exception:
        current_app.logger.exception('pump-status websocket error')
        return

def _water_level_status(sensor):
    height = sensor.get_water_level_difference_cm()
    if height is None:
        percentage = None
    elif sensor.resevoir_depth <= 0:
        percentage = None
    else:
        percentage = round((height / sensor.resevoir_depth) * 100, 1)
        percentage = max(0.0, min(100.0, percentage))
    return {
        'id': sensor.id,
        'water_height': height,
        'water_level_percentage': percentage,
    }


@bp.websocket('/water-level')
async def water_level():
    try:
        while True:
            statuses = []
            for sensor in list(loaded_water_level_sensors.values()):
                statuses.append(await asyncio.to_thread(_water_level_status, sensor))
            await websocket.send(json.dumps(statuses))
            if await _wait_for_stop():
                return
    except asyncio.CancelledError:
        raise
    except Exception:
        current_app.logger.exception('water-level websocket error')
        return

# Test routes
async def loaded_pump_from_form():
    form = await request.form
    try:
        return loaded_pumps.get(int(form.get('pump_id')))
    except (TypeError, ValueError):
        return None


@bp.route('/test-water', methods=['POST'])
async def test_water():
    pump = await loaded_pump_from_form()
    if pump is None:
        await flash("Pump not found")
        return redirect(url_for('autowater.tests'))
    test_quantity = 200
    current_app.add_background_task(pump.run_water_pump, test_quantity)
    await flash(f"Pump test - dispensing {test_quantity}ml")
    return redirect(url_for('autowater.tests'))

@bp.route('/turn-on-pump', methods=['POST'])
async def turn_on_pump():
    pump = await loaded_pump_from_form()
    if pump is None:
        await flash("Pump not found")
        return redirect(url_for('autowater.tests'))
    if pump.is_running():
        await flash("Pump is already running")
        return redirect(url_for('autowater.tests'))
    if not pump.turn_on():
        await flash("Failed to turn on pump")
        return redirect(url_for('autowater.tests'))
    return redirect(url_for('autowater.tests'))

@bp.route('/turn-off-pump', methods=['POST'])
async def turn_off_pump():
    pump = await loaded_pump_from_form()
    if pump is None:
        await flash("Pump not found")
        return redirect(url_for('autowater.tests'))
    if not pump.turn_off():
        await flash("Failed to turn off pump")
        return redirect(url_for('autowater.tests'))
    return redirect(url_for('autowater.tests'))
