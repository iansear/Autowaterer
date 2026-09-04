from quart import Quart
from .config.pump_config import init_pump_1
from .config.schedule_config import scheduler

def create_app():
    app = Quart(__name__, instance_relative_config=True)
    from .routes.autowater import bp
    app.register_blueprint(bp)
    init_pump_1()
    scheduler.start()
    return app
