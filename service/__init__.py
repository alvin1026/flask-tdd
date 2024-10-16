import sys
from flask import Flask
from service import config
from service.common import log_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    from service.models import db
    db.init_app(app)

    with app.app_context():
        from service import routes, models
        from service.common import error_handlers, cli_commands
        try:
            models.init_db()
        except Exception as error:
            app.logger.critical("%s: Cannot continue", error)
            # gunicorn requires exit code 4 to stop spawning workers when they die
            sys.exit(4)

        log_handlers.init_logging(app, "gunicorn.error")

        app.logger.info(70 * "*")
        app.logger.info(" EMPLOYEE MANAGEMENT SERVICE ".center(70, "*"))
        app.logger.info(70 * "*")
        app.logger.info("Service initialized!")

        return app
