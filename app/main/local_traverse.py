#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import re
from app import db
from app.models import Movie
from instance.config import Config


def traverse(disk, queue):
    disk_path = disk + ':'
    for root, dirs, files in os.walk(disk_path):
        for i, dirname in enumerate(dirs):
            if dirname == '0':
                break
            for tag in Config.TARGET_FILES:
                if dirname.find(tag) != -1:
                    info = analyze(dirname)
                    if info:
                        info.append(dirname)
                        info.append(get_size(os.path.join(root, dirname)))
                        info.append(1)
                        queue.put(info)
                        print "%s, %s, %s, %.2f" % (info[0], info[1], info[2].decode('gbk'), info[3])
                    # if info:
                    #     m = Movie(
                    #         title=info[0],
                    #         date=info[1],
                    #         size=dir_size
                    #     )
                    #     db.session.add(m)
                    break
            if dirname.lower() not in Config.TARGET_DIRS:
                dirs[i] = '0'
        for j, filename in enumerate(files):
            for tag in Config.TARGET_EXTS:
                if filename.find(tag) != -1:
                    for tag2 in Config.TARGET_FILES:
                        if filename.find(tag2) != -1:
                            info = analyze(filename)
                            if info:
                                info.append(filename)
                                info.append(get_size(os.path.join(root, filename)))
                                info.append(1)
                                queue.put(info)
                                print "%s, %s, %s, %.2f" % (
                                    info[0], info[1], info[2].decode('gbk'), info[3])
                            break
                    break


def analyze(name):
    pattern_film = r'(.+?)[\s\.](19\d\d|20\d\d)'
    info = re.search(pattern_film, name)
    if info:
        return [info.group(1).decode('gbk'),
                info.group(2).decode('gbk')]
    else:
        return False


def get_size(path):
    size = 0L
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    if os.path.isfile(path):
        size = os.path.getsize(path)
    return size/1024/1024/1024


def update_db():
    pass
