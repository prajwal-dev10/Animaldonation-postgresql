from flask import Flask
from .extensions import db, login_manager
import os


def create_app():

    base_dir = os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))
    )


    app = Flask(
        __name__,
        template_folder=os.path.join(
            base_dir,
            "templates"
        ),
        static_folder=os.path.join(
            base_dir,
            "static"
        )
    )


    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "saveanimal123"
    )


    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@db:5432/animaldb"
    )


    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    app.config["UPLOAD_FOLDER"] = os.path.join(
        base_dir,
        "static/uploads"
    )


    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )


    db.init_app(app)

    login_manager.init_app(app)


    from .routes import main

    app.register_blueprint(main)


    return app