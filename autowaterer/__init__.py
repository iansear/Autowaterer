from quart import Quart


def create_app():
    app = Quart(__name__, instance_relative_config=True)
    from .routes.autowater import bp
    app.register_blueprint(bp)
    return app
