#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask import Flask
from instance.config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
