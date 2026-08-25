from quart import Quart
from .tasks import tasks

def create_app():
    app = Quart(__name__, instance_relative_config=True)
    from .routes.autowater import bp
    tasks.init_app(app)
    app.register_blueprint(bp)
    return app
