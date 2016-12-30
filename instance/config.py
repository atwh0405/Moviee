#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

basedir = os.path.abspath(os.path.dirname('__name__'))
PROXY_SITES = [
    'http://www.kuaidaili.com/free/inha/1',
    'http://www.kuaidaili.com/free/inha/2',
    'http://www.kuaidaili.com/free/inha/3',
    'http://www.kuaidaili.com/free/inha/4',
    'http://www.kuaidaili.com/free/inha/5',
    'http://www.kuaidaili.com/free/inha/6',
    'http://www.kuaidaili.com/free/inha/7',
    'http://www.kuaidaili.com/free/inha/8',
    'http://www.kuaidaili.com/free/inha/9',
    'http://www.kuaidaili.com/free/inha/10'
]
PROXY_REGEX = r'<td data-title="IP">(.*?)</td>.*?<td data-title="PORT">(.*?)</td>'
REFERER_LIST = [
    'https://www.google.com/',
    'https://www.baidu.com/',
    'https://cn.bing.com/',
    'https://www.sogou.com/'
]
TIMEOUT = 10
PATTERN_1 = r'<p class="ul first">.*?<div class="pl2">.*?'
PATTERN_1 += r'<a.*?"(https://movie.douban.com/subject/.*?)\".*?>(.*?)\/.*?<span.*?>(.*?)</span>'
PATTERN_1 += r'.*?<p class="pl">(.*?)</p>'
PATTERN_1 += r'.*?rating_nums">(.*?)</span>.*?pl">\((.*?)\)</span>'
PATTERN_2 = r'<a class="nbgnbg".*?<img src=(.*?)\stitle.*?>'
USERNAME = 'at.wh0405@163.com'
PASSWORD = 'wanghan0710'

class Config():
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TARGET_DIRS = ['pt', 'ttg', '迅雷下载', 'xunlei', 'cmct', 'hd4fans',
                   'hdc', 'hdr', 'hdsky', 'hdtime', 'mt', 'shenzhan',
                   'hdhome', 'keepfrds', '']
    TARGET_FILES = ['BluRay', '1080p', '1080i', '720p', 'x265', 'x264']
    TARGET_EXTS = ['avi', 'bdmv', 'divx', 'hdmov', 'm2t', 'm2ts', 'mkv',
               'mp4', 'mpeg', 'mpg', 'mpls', 'mov', 'mts', 'rmvb',
               'tp', 'ts', 'vob', 'wm', 'wmv']

    @staticmethod
    def init_app(app):
        pass


class ProductionCofig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_BINDS = {
        'proxy': 'sqlite:///' + os.path.join(basedir, 'proxy.sqlite')
    }

config = {
    'production': ProductionCofig
}