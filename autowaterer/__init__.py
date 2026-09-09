import asyncio
import os
import signal
from quart import Quart
from dotenv import load_dotenv
from sqlalchemy import select
from .classes.pump import Pump as HardwarePump
from .config.pump_config import loaded_pumps, stop_all_pumps
from .config.schedule_config import scheduler
from .db import db
from .db.user import User
from .db.job import Job
from .db.pump import Pump

def create_app():
    app = Quart(__name__, instance_relative_config=True)
    load_dotenv()
    app.secret_key = os.environ.get("QUART_SECRET_KEY", "fallback-not-so-secret-key")
    db.init_app(app)
    app.config["BACKGROUND_TASK_SHUTDOWN_TIMEOUT"] = 2
    from .routes.autowater import bp
    app.register_blueprint(bp)

    @app.before_serving
    async def start_scheduler():
        if not scheduler.running:
            scheduler.start()
            print('Scheduler started...')

    @app.before_serving
    async def stop_pumps_on_shutdown():
        loop = asyncio.get_running_loop()
        stop = asyncio.Event()
        app.extensions["stop_serving"] = stop

        def request_stop():
            if not stop.is_set():
                print('Interrupt pumps for shutdown...')
                stop.set()
            stop_all_pumps()

        def wrap_signal(sig):
            handlers = getattr(loop, "_signal_handlers", None)
            existing = handlers.get(sig) if handlers else None
            callback = getattr(existing, "_callback", None)
            args = getattr(existing, "_args", ()) or ()

            def handler():
                request_stop()
                if callback is not None:
                    callback(*args)
                elif sig == signal.SIGINT:
                    os.kill(os.getpid(), signal.SIGTERM)

            try:
                loop.add_signal_handler(sig, handler)
            except (NotImplementedError, RuntimeError):
                pass

        wrap_signal(signal.SIGINT)
        if hasattr(signal, "SIGTERM"):
            wrap_signal(signal.SIGTERM)

        async def _stop_pumps():
            stop_task = asyncio.create_task(stop.wait())
            shutdown_task = asyncio.create_task(app.shutdown_event.wait())
            try:
                await asyncio.wait(
                    {stop_task, shutdown_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )
            finally:
                for task in (stop_task, shutdown_task):
                    if not task.done():
                        task.cancel()
            request_stop()

        app.add_background_task(_stop_pumps)

    @app.before_serving
    async def setup_db():
        await db.create_all()
        print('Database created...')


    @app.before_serving
    async def load_pumps():
        async with db.bind.Session() as session:
            pumps = (await session.scalars(select(Pump))).all()
            pump_rows = [
                (pump.id, pump.name, pump.gpio_pin, pump.rate) for pump in pumps
            ]
        for pump_id, name, gpio_pin, rate in pump_rows:
            loaded_pumps[pump_id] = HardwarePump(gpio_pin, rate)
            print(f'Pump {name} loaded...')

    @app.before_serving
    async def load_jobs():
        async with db.bind.Session() as session:
            jobs = (await session.scalars(select(Job))).all()

        for job in jobs:
            hardware_pump = loaded_pumps.get(job.pump_id)
            func = getattr(hardware_pump, job.function, None) if hardware_pump else None
            if func is None:
                print(f'Skipping job {job.name}: unknown pump or function')
                continue
            scheduler.add_job(
                func,
                id=str(job.id),
                name=job.name,
                trigger=job.trigger,
                hour=job.hour,
                minute=job.minute,
                args=job.args,
                replace_existing=True,
            )
            print(f'Job {job.name} loaded...')

    @app.after_serving
    async def shutdown_hardware():
        if scheduler.running:
            scheduler.shutdown(wait=False)
            print('Scheduler stopped...')
        stop_all_pumps()
        for pump in list(loaded_pumps.values()):
            try:
                pump.close()
            except Exception as e:
                print(f'Error closing pump: {e}')
        loaded_pumps.clear()
        print('Pumps closed...')

    return app
