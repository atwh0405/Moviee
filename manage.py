#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Movie, Proxy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

app = create_app('production')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Movie=Movie, Proxy=Proxy)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
