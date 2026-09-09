import os
from quart import Quart
from dotenv import load_dotenv
from sqlalchemy import select
from .config.pump_config import get_job_functions, init_pump_1
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
    init_pump_1()
    from .routes.autowater import bp
    app.register_blueprint(bp)

    @app.before_serving
    async def start_scheduler():
        if not scheduler.running:
            scheduler.start()
            print('Scheduler started...')

    @app.before_serving
    async def setup_db():
        await db.create_all()
        print('Database created...')

    @app.before_serving
    async def load_jobs():
        job_functions = get_job_functions()
        async with db.bind.Session() as session:
            jobs = (await session.scalars(select(Job))).all()

        for job in jobs:
            func = job_functions.get(job.function)
            if func is None:
                print(f'Skipping job {job.name}: unknown function {job.function!r}')
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
    async def stop_scheduler():
        if scheduler.running:
            scheduler.shutdown(wait=False)
            print('Scheduler stopped...')

    return app
