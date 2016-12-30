#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import db
from time import sleep
from requests import Timeout, ConnectionError
import re
import copy
from bs4 import BeautifulSoup
import requests
import webbrowser
from ..utils import get_user_agent, fetch
from instance.config import TIMEOUT, PATTERN_1, PATTERN_2,  USERNAME, PASSWORD
from ..models import Proxy, Movie
from gevent import GreenletExit
from gevent.queue import Queue, Empty
from gevent.pool import Pool
from gevent import monkey, joinall, spawn
from gevent.lock import BoundedSemaphore
from sqlite3 import Error, IntegrityError
monkey.patch_all()


class Crawler():

    def __init__(self):
        self.search_url = 'https://movie.douban.com/subject_search?search_text='
        self.p1 = r'<a class="nbg" href="(https://movie.douban.com/subject/.*?)".*?>'
        self.p2 = PATTERN_2
        self.ua = get_user_agent()
        self.login_url = 'https://www.douban.com/accounts/login?source=movie'

    def if_captcha(self):
        login_request = fetch('https://www.douban.com/accounts/login?source=movien', s)
        soup = BeautifulSoup(login_request.text, 'lxml')
        if soup.find(class_='captcha_block') is not None:
            return soup
        else:
            return False

    def get_captcha_img(self, soup):
        return soup.find(id='captcha_image').attrs['src']

    def login(self):
        formdata = {
            'source': 'movie',
            'redir': 'https://movie.douban.com',
            'form_email': USERNAME,
            'form_password': PASSWORD,
            'login': u'登录'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
        }
        s = requests.Session()
        global s
        if_cap = self.if_captcha()
        if if_cap:
            print u'本次登录需要输入验证码'
            i = 1
            while i <= 5:
                webbrowser.open_new_tab(self.get_captcha_img(if_cap))
                captcha_id = if_cap.find(id='captcha_block').find_next_sibling().find_next_sibling().attrs['value']
                print captcha_id
                captcha_solution = raw_input('Please input the captcha:')
                formdata.update({'captcha-solution': captcha_solution})
                formdata.update({'captcha-id': captcha_id})
                print formdata
                r = s.post(self.login_url, data=formdata, headers=headers)
                soup = BeautifulSoup(r.text, 'lxml')
                if soup.find(class_='nav-user-account') is not None:
                    print u'登录成功！'
                    return True
                else:
                    print u'登录失败，尝试重新获取验证码...'
                    i += 1
        r = s.post(self.login_url, data=formdata, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        if soup.find(class_='nav-login') is None:
            print u'登录成功！'
            return True
        else:
            print u'登录失败，请检查用户名和密码！'
            return False

    def get_movie_info(self, p, subject):
        info = subject[1]
        if subject[0] is None:
            if info[4] == 3:
                movie = Movie(
                    date=info[1].decode('gbk'),
                    filename=info[2].decode('gbk'),
                    info_complete=False)
                return movie
            else:
                return False

        main_match = fetch(subject[0], s, proxy=p.get())
        soup = BeautifulSoup(main_match.text, 'lxml')

        print subject[0]
        brief = soup.find(property="v:summary").text if soup.find(property="v:summary") is not None else u''
        score = soup.find(property="v:average").text if soup.find(property="v:average") is not None else 0
        evaluate_num = soup.find(property="v:votes").text if soup.find(property="v:votes") is not None else 0
        print info[0], evaluate_num
        actor_list = soup.find(class_="actor").select('a[rel="v:starring"]') if soup.find(class_="actor") is not None \
            else []
        actor = [i.text for i in actor_list] if actor_list else []
        actor = ','.join(actor)
        title = soup.find(property="v:itemreviewed").text if soup.find(property="v:itemreviewed") is not None else u''
        poster_url = soup.find(class_="nbgnbg").find('img').attrs['src']
        movie = Movie(
            title=title,
            eng_title=info[0],
            filename=info[2].decode('gbk'),
            subject_id=subject[0],
            brief=brief.strip(),
            date=int(info[1].decode('gbk')),
            score=score,
            evaluate_num=int(evaluate_num) if evaluate_num else 0,
            actor=actor,
            size=info[3],
            poster_url=poster_url,
            info_complete=True
        )
        return movie

    def get_movie_subject(self, info, q, p, retry=0, sep=None):
        if sep is not None:
            url_text = self.search_url + info[0] + '.' + info[1]
        else:
            url_text = self.search_url + info[0] + ' ' + info[1]
        # proxy = Proxy.get_random_proxy()
        while retry <= 5:
            try:
                subject_search = fetch(url_text, s, proxy=p.get())
                break
            except (Timeout, ConnectionError):
                sleep(1)
                retry += 1
            # try:
            #     if proxy:
            #         db.session.delete(proxy)
            #         db.session.commit()
            # except Error:
            #     pass
        # if retry == 6:
        #     q.put(info)
        #     raise GreenletExit

        # try:
        #     db.session.add(movie)
        # except (Error, IntegrityError):
        #     pass
        subject_match = re.search(self.p1, subject_search.text, re.S)

        # soup = BeautifulSoup(subject_search.text, 'lxml')
        # subject = soup.find(class_="nbg").attrs['href']
        # evaluate_num = soup.find(class_="star clearfix").find(class_="pl").text
        if subject_match is not None:
            return subject_match.group(1), info
        else:
            info[4] += 1
            if info[4] == 2:
                queue2.put(info)
                # info[4]的值会在第二次查询过程中改变为3，因此用深拷贝进行备份第一次查询的值2.
                info_current = copy.deepcopy(info)
                return self.get_movie_queue(queue2, movies, p), info_current
            else:
                return None, info

    def get_movie_queue(self, q, m, p):
        while 1:
            try:
                info = q.get(False)
            except Empty:
                break
            if q == queue:
                result = self.get_movie_info(p, self.get_movie_subject(info, q, p))
            elif q == queue2:
                result = self.get_movie_info(p, self.get_movie_subject(info, q, p, sep=True))
            # sem.acquire()
            if result:
                m.put(result, False)
            # sem.release()
            sleep(0)


sem = BoundedSemaphore(1)
pool = Pool(5)
queue = Queue()
movies = Queue()
proxies = Queue()
crawler = Crawler()
# 存放第一次查询没有结果的电影info，以备将分隔符改为"."后进行第二次查询
queue2 = Queue()


def crawl_with_gevent():

    from local_traverse import traverse
    traverse('f', queue)

    for _ in range(300):
        proxies.put(Proxy.get_random_proxy().address)
    if not crawler.login():
        print u'未登录成功！'
        return False
    # while pool.free_count():
    #     sleep(0.1)
    #     pool.spawn(crawler.get_movie_queue, queue, movies, proxies)
    # pool.join()
    joinall([
        spawn(crawler.get_movie_queue, queue, movies, proxies),
        spawn(crawler.get_movie_queue, queue, movies, proxies),
        spawn(crawler.get_movie_queue, queue, movies, proxies),
        spawn(crawler.get_movie_queue, queue, movies, proxies),
    ])
    # joinall([
    #     spawn(crawler.get_movie_queue, queue2, movies, proxies),
    # ])

    while 1:
        try:
            db.session.add(movies.get(timeout=0))
        except Empty:
            break
    db.session.commit()

