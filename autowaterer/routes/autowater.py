from quart import Blueprint, current_app, flash, render_template, redirect, url_for, request, websocket
from datetime import datetime
import asyncio
import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..classes.pump import Pump as HardwarePump
from ..config.pump_config import loaded_pumps
from ..config.schedule_config import scheduler
from ..db import db
from ..db.job import Job
from ..db.pump import Pump

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
    # return redirect(url_for('autowater.dashboard'))

# Page routes
@bp.route('/dashboard')
async def dashboard():
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.strftime('%Y-%m-%d %H:%M')
        })
    return await render_template('dashboard.html', jobs=jobs)

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
        flash('Name, pump, time, and quantity are required!')
        return await render_template('create_job.html', pumps=pumps)

    try:
        pump_id = int(pump_id)
        quantity = float(quantity)
        if quantity <= 0:
            flash('Quantity must be greater than 0.')
            return await render_template('create_job.html', pumps=pumps)

        hardware_pump = loaded_pumps.get(pump_id)
        if hardware_pump is None:
            flash('Unknown pump.')
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
        flash(f"Error scheduling water: {e}")
        return await render_template('create_job.html', pumps=pumps)

    return redirect(url_for('autowater.schedule'))

@bp.route('/delete-job', methods=['POST'])
async def delete_job():
    form = await request.form
    job_id = form.get('job_id')
    if not job_id:
        flash('Job id is required!')
        return redirect(url_for('autowater.index'))

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

    return redirect(url_for('autowater.index'))

# Pump routes
@bp.route('/create-pump', methods=['GET', 'POST'])
async def create_pump():
    if request.method == 'GET':
        return await render_template('create_pump.html')

    form = await request.form
    name = form.get('name')
    description = form.get('description')
    gpio_pin = int(form.get('gpio_pin'))
    rate = float(form.get('rate'))
    pump = Pump(name=name, description=description, gpio_pin=gpio_pin, rate=rate)
    async with db.bind.Session() as session:
        async with session.begin():
            session.add(pump)
            await session.flush()
            loaded_pumps[pump.id] = HardwarePump(gpio_pin, rate)
    return redirect(url_for('autowater.pumps'))

@bp.route('/delete-pump', methods=['POST'])
async def delete_pump():
    form = await request.form
    pump_id = form.get('pump_id')
    if not pump_id:
        flash('Pump id is required!')
        return redirect(url_for('autowater.pumps'))
    pump = await db.get(Pump, pump_id)
    if pump:
        await db.delete(pump)
    return redirect(url_for('autowater.pumps'))

# Web Socket
@bp.websocket('/pump-status')
async def pump_status():
    try:
        while True:
            statuses = []
            for pump_id, hardware_pump in loaded_pumps.items():
                statuses.append({
                    'id': pump_id,
                    'running': hardware_pump.is_running(),
                    'elapsed': hardware_pump.get_time_elapsed(),
                })
            await websocket.send(json.dumps(statuses))
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        raise
    except Exception:
        return

# Test routes
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
