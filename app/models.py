#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from app import db
from random import randint


class Movie(db.Model):
    __tablename_ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(64))
    eng_title = db.Column(db.Unicode(64))
    brief = db.Column(db.UnicodeText)
    date = db.Column(db.Integer, index=True)
    score = db.Column(db.Integer, index=True)
    size = db.Column(db.Integer, index=True)
    evaluate_num = db.Column(db.Integer, index=True)
    poster_url = db.Column(db.String(128))
    subject_id = db.Column(db.Unicode(128))
    actor = db.Column(db.UnicodeText)
    info_complete = db.Column(db.Boolean, default=True)
    filename = db.Column(db.Unicode(128))


class Proxy(db.Model):
    # 用bind连接多个数据库，db.create_all 和 db.drop_all方法需要指定bind='proxy'
    __bind_key__ = 'proxy'
    __tablename__ = 'proxies'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(32), unique=True)

    def __repr__(self):
        return '<Address: %r>' % self.address

    @classmethod
    def get_random_proxy(cls):
        proxy = cls.query.filter_by(id=randint(1, 30)).first()
        return proxy
