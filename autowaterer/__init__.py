import os
from quart import Quart
from dotenv import load_dotenv
from .config.pump_config import init_pump_1
from .config.schedule_config import scheduler

def create_app():
    app = Quart(__name__, instance_relative_config=True)
    load_dotenv()
    app.secret_key = os.environ.get("QUART_SECRET_KEY", "fallback-not-so-secret-key")
    init_pump_1()
    from .routes.autowater import bp
    app.register_blueprint(bp)

    @app.before_serving
    async def start_scheduler():
        if not scheduler.running:
            scheduler.start()
            print('Scheduler started...')

    @app.after_serving
    async def stop_scheduler():
        if scheduler.running:
            scheduler.shutdown(wait=False)
            print('Scheduler stopped...')

    return app
