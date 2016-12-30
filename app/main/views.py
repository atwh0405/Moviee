#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import main
from flask import render_template
from crawler import Crawler, crawl_with_gevent


@main.route('/')
def index():
    crawl_with_gevent()
    return render_template('main/index.html')