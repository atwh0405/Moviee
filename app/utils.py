#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import re
import requests
from fake_useragent import UserAgent
from app.models import Proxy
from app import db
from instance.config import REFERER_LIST, TIMEOUT, PROXY_REGEX, PROXY_SITES
from sqlite3 import IntegrityError
import threading
import time
# from multiprocessing.dummy import Pool as ThreadPool
from gevent.pool import Pool as GPool
from requests.exceptions import RequestException


def get_referer():
    return random.choice(REFERER_LIST)


def get_user_agent():
    # 程序开始时将static下的fake_useragent.json复制到tempfile.gettempfile()
    ua = UserAgent()
    return ua.random


def fetch(url, session, proxy=None):
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
    # }
    proxies = None
    if proxy is not None:
        proxies = {'http': proxy}
    return session.get(url, proxies=proxies)


def save_proxy(url):
    try:
        r = fetch(url)
    except requests.exceptions.RequestException:
        return False
    print url
    print r
    addresses = re.findall(PROXY_REGEX, r.text, re.S)
    print len(addresses)
    for ip_port in addresses:
        address = ip_port[0] + ':' + ip_port[1]
        proxy = Proxy(address=address)
        print 'saving address: %s' % address
        db.session.add(proxy)
        try:
            db.session.commit()
            print 'commit'
        except:
            print 'commit failed'
            db.session.rollback()


def clean_up():
    db.drop_all(bind='proxy')
    db.create_all(bind='proxy')


def get_proxies():
    clean_up()
    for url in PROXY_SITES:
        save_proxy(url)
        time.sleep(1)
    # 若使用pool.map方法会导致db实例没有绑定错误
    # for i in range(len(PROXY_SITES)):
    # 注意单个参数以元组方式输入
    #    pool.apply_async(save_proxy, (PROXY_SITES[i],))
    #    print 'start url %r' % i
    # pool.map(save_proxy, PROXY_SITES)
    # pool.close()
    # pool.join()


def check_proxy(p):
    try:
        fetch('https://www.baidu.com', proxy=p.address)
        print 'succeed'
    except RequestException:
        print 'bad address'
        db.session.delete(p)
        db.session.commit()


def remove_unavailable_proxy():
   gpool = GPool(10)
   gpool.map(check_proxy, Proxy.query.all())
